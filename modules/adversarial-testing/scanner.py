import os
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import logging
import requests
import numpy as np
import tensorflow as tf
import torch
from art.estimators.classification.scikitlearn import ScikitlearnSVC
from art.estimators.classification import (
    TensorFlowV2Classifier,
    PyTorchClassifier,
    SklearnClassifier,
    BlackBoxClassifier
)
from art.attacks.evasion import (
    FastGradientMethod,
    ProjectedGradientDescent,
    CarliniL2Method,
    DeepFool,
    BoundaryAttack,
    HopSkipJump,
    ZooAttack
)
from art.attacks.extraction import (
    CopycatCNN,
    KnockoffNets
)
from art.attacks.poisoning import (
    PoisoningAttackBackdoor,
    PoisoningAttackSVM
)

logger = logging.getLogger(__name__)

class AdversarialScanner:
    """
    Adversarial robustness testing scanner using ART.
    Supports both file-based models and REST endpoints.
    """
    
    SUPPORTED_FRAMEWORKS = ['tensorflow', 'pytorch', 'sklearn']
    
    def __init__(self):
        self.classifier = None
        self.framework = None
        self.is_blackbox = False
        self._setup_attacks()
        
    def _setup_attacks(self):
        """Initialize different types of attacks based on classifier type."""

        def create_backdoor_pattern(x: np.ndarray) -> np.ndarray:
            """Create a backdoor pattern - adds a small trigger pattern to the input."""
            poison_x = x.copy()
            # Add a small pattern in the corner - assumes image data
            if len(x.shape) == 4:  # (batch_size, height, width, channels)
                poison_x[:, -3:, -3:, :] = 1.0
            else:  # Handle other data shapes appropriately
                poison_x = poison_x + 0.1
            return poison_x
        
        # Common attack parameters
        self.attack_params = {
            'eps': 0.2,
            'batch_size': 32,
            'nb_epochs': 5,
            'max_iter': 50
        }
        
        # Attacks for white-box (model file) testing
        self.whitebox_attacks = {
            'evasion': {
                'fgsm': lambda clf: FastGradientMethod(
                    estimator=clf, 
                    eps=self.attack_params['eps']
                ),
                'pgd': lambda clf: ProjectedGradientDescent(
                    estimator=clf,
                    eps=self.attack_params['eps'],
                    max_iter=self.attack_params['max_iter']
                ),
                'carlini': lambda clf: CarliniL2Method(
                    classifier=clf,
                    max_iter=self.attack_params['max_iter']
                ),
                'deepfool': lambda clf: DeepFool(classifier=clf)
            },
            'extraction': {
                'copycat': lambda clf: CopycatCNN(
                    classifier=clf,
                    batch_size_fit=self.attack_params['batch_size'],
                    batch_size_query=self.attack_params['batch_size'],
                    nb_epochs=self.attack_params['nb_epochs']
                ),
                'knockoff': lambda clf: KnockoffNets(
                    classifier=clf,
                    batch_size_fit=self.attack_params['batch_size'],
                    batch_size_query=self.attack_params['batch_size'],
                    nb_epochs=self.attack_params['nb_epochs']
                )
            },
            'poisoning': {
                'backdoor': lambda clf: PoisoningAttackBackdoor(
                    perturbation=create_backdoor_pattern
                )
            }
        }
        
        # Attacks for black-box (REST endpoint) testing
        self.blackbox_attacks = {
            'evasion': {
                'boundary': lambda clf: BoundaryAttack(
                    estimator=clf,  
                    targeted=False,  # Set to untargeted attack
                    max_iter=self.attack_params['max_iter']
                ),
                'hopskipjump': lambda clf: HopSkipJump(
                    classifier=clf,  # Use classifier instead of estimator
                    max_iter=self.attack_params['max_iter'],
                    max_eval=100,
                    targeted=False  # Set to untargeted attack
                ),
                'zoo': lambda clf: ZooAttack(
                    classifier=clf,
                    max_iter=self.attack_params['max_iter'],
                    batch_size=1,
                    use_resize=False
                )
            },
            'extraction': {
                'copycat': lambda clf: CopycatCNN(
                    classifier=clf,
                    batch_size_fit=self.attack_params['batch_size'],
                    batch_size_query=self.attack_params['batch_size'],
                    nb_epochs=self.attack_params['nb_epochs']
                ),
                'knockoff': lambda clf: KnockoffNets(
                    classifier=clf,
                    batch_size_fit=self.attack_params['batch_size'],
                    batch_size_query=self.attack_params['batch_size'],
                    nb_epochs=self.attack_params['nb_epochs']
                )
            },
            'poisoning': {
                'backdoor': lambda clf: PoisoningAttackBackdoor(
                    perturbation=create_backdoor_pattern
                )
            }
        }

    def _create_substitute_model2(self, clf: Any) -> Optional[Any]:
        """Create a substitute model architecture for extraction attacks."""
        if isinstance(clf, TensorFlowV2Classifier):
            # Create model architecture suitable for image data
            model = tf.keras.Sequential([
                tf.keras.layers.Input(shape=clf.input_shape),
                tf.keras.layers.Flatten(),  # Flatten the image input
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(clf.nb_classes, activation='softmax')
            ])
            
            # Define custom training step
            @tf.function
            def train_step(model: tf.keras.Model, 
                         x_batch: tf.Tensor, 
                         y_batch: tf.Tensor) -> tf.Tensor:
                with tf.GradientTape() as tape:
                    y_pred = model(x_batch, training=True)
                    loss = tf.keras.losses.CategoricalCrossentropy()(y_batch, y_pred)
                
                gradients = tape.gradient(loss, model.trainable_variables)
                optimizer.apply_gradients(zip(gradients, model.trainable_variables))
                return loss

            # Create optimizer
            optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
            
            # Create ART classifier
            substitute = TensorFlowV2Classifier(
                model=model,
                nb_classes=clf.nb_classes,
                input_shape=clf.input_shape,
                loss_object=tf.keras.losses.CategoricalCrossentropy(),
                optimizer=optimizer,
                train_step=train_step
            )
            return substitute
        return None
    
    def _create_substitute_model(self, clf: Any) -> Optional[Any]:
        """Create a substitute model for extraction attacks."""
        # For blackbox/REST classifiers, we can infer input shape from classifier
        input_shape = clf.input_shape
        nb_classes = clf.nb_classes
        
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=input_shape),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(nb_classes, activation='softmax')
        ])
        
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
        model.compile(
            optimizer=optimizer,
            loss=tf.keras.losses.CategoricalCrossentropy(),
            metrics=['accuracy']
        )
        
        substitute = TensorFlowV2Classifier(
            model=model,
            nb_classes=nb_classes,
            input_shape=input_shape,
            loss_object=tf.keras.losses.CategoricalCrossentropy(),
            optimizer=optimizer
        )
        return substitute

    def load_model(self, file_path: Path, framework: str) -> None:
        """Load a model from file."""
        if framework not in self.SUPPORTED_FRAMEWORKS:
            raise ValueError(f"Unsupported framework: {framework}")
            
        try:
            self.framework = framework
            self.is_blackbox = False
            
            if framework == 'tensorflow':
                model = tf.keras.models.load_model(file_path)
                self.classifier = TensorFlowV2Classifier(
                    model=model,
                    nb_classes=model.output_shape[-1],
                    input_shape=model.input_shape[1:],
                    loss_object=tf.keras.losses.CategoricalCrossentropy()
                )
            elif framework == 'pytorch':
                model = torch.load(file_path)
                self.classifier = PyTorchClassifier(
                    model=model,
                    loss=torch.nn.CrossEntropyLoss(),
                    input_shape=model.input_shape,
                    nb_classes=model.num_classes
                )
            elif framework == 'sklearn':
                import joblib
                model = joblib.load(file_path)
                self.classifier = SklearnClassifier(model=model)
                
            self.classifier.model_file = file_path
                
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")

    def setup_endpoint(
        self,
        endpoint_url: str,
        input_shape: Tuple,
        nb_classes: int,
        request_format: Optional[Dict] = None,
        response_key: Optional[str] = None,
        headers: Optional[Dict] = None
    ) -> None:
        """Setup classifier for REST endpoint."""
        try:
            # Create prediction function for the endpoint
            def predict_fn(x):
                data = request_format.copy() if request_format else {}
                if request_format and "<input>" in str(request_format):
                    # Handle template replacement
                    data = {k: v.replace("<input>", str(x.tolist())) if isinstance(v, str) else v 
                           for k, v in request_format.items()}
                else:
                    data = {"instances": x.tolist()}

                response = requests.post(
                    endpoint_url,
                    json=data,
                    headers=headers or {"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                if response_key:
                    for key in response_key.split('.'):
                        result = result[key]
                return np.array(result)

            # Create black-box classifier
            self.classifier = BlackBoxClassifier(
                predict_fn=predict_fn,
                input_shape=input_shape,
                nb_classes=nb_classes,
                clip_values=(0, 1)  # Assume normalized inputs
            )
            self.classifier.endpoint_url = endpoint_url
            self.is_blackbox = True
            
        except Exception as e:
            raise RuntimeError(f"Failed to setup endpoint classifier: {str(e)}")

    def _get_applicable_attacks(self):
        """Get attacks applicable to current classifier type."""
        return self.blackbox_attacks if self.is_blackbox else self.whitebox_attacks

    def _is_sklearn_classifier(self, clf) -> bool:
        """Helper method to safely check if classifier is SklearnClassifier."""
        try:
            return isinstance(clf, SklearnClassifier)
        except Exception:
            return False
        
    def run_attacks(
        self, 
        attack_type: str, 
        x_test: np.ndarray, 
        y_test: Optional[np.ndarray] = None
    ) -> List[Dict]:
        """Run specified type of attacks."""
        if self.classifier is None:
            raise ValueError("Classifier not initialized. Call load_model() or setup_endpoint() first.")
            
        results = []
        attacks = self._get_applicable_attacks().get(attack_type, {})

        for name, attack_fn in attacks.items():
            try:
                # Create the attack
                attack = attack_fn(self.classifier)
                
                if attack_type == 'evasion':
                    if y_test is None:
                        raise ValueError("y_test required for evasion attacks")
                    x_test_adv = attack.generate(x=x_test)
                    predictions = self.classifier.predict(x_test_adv)
                    success_rate = 1 - np.mean(
                        np.argmax(predictions, axis=1) == np.argmax(y_test, axis=1)
                    )
                    
                elif attack_type == 'extraction':
                    # Create substitute model
                    substitute = self._create_substitute_model(self.classifier)
                    if substitute is None:
                        raise ValueError("Could not create substitute model for extraction attack")
                    
                    # Run extraction with limited dataset and our substitute model
                    x_test_subset = x_test[:min(1000, len(x_test))]
                    extracted_model = attack.extract(
                        x=x_test_subset,
                        thieved_classifier=substitute  # Pass as kwarg to extract()
                    )
                    
                    # Compare predictions
                    orig_preds = self.classifier.predict(x_test_subset)
                    stolen_preds = extracted_model.predict(x_test_subset)
                    success_rate = np.mean(
                        np.argmax(orig_preds, axis=1) == np.argmax(stolen_preds, axis=1)
                    )
                        
                else:  # poisoning
                    if y_test is None:
                        raise ValueError("y_test required for poisoning attacks")
                    
                    if name == 'backdoor':
                        # Create poisoned data
                        max_samples = min(100, len(x_test))
                        x_subset = x_test[:max_samples]
                        y_subset = y_test[:max_samples]
                        
                        # Get predictions on clean data first
                        clean_preds = self.classifier.predict(x_subset)
                        
                        # Create poisoned data with backdoor pattern
                        poisoned_data, poisoned_labels = attack.poison(x_subset, y_subset)
                        
                        # Get predictions on poisoned data
                        poison_preds = self.classifier.predict(poisoned_data)
                        
                        # Success means the predictions changed for poisoned inputs
                        # but we want the model to maintain accuracy on clean inputs
                        success_rate = np.mean(
                            np.argmax(poison_preds, axis=1) != np.argmax(clean_preds, axis=1)
                        )
                    else:
                        # Handle other poisoning attacks (like SVM) differently
                        max_samples = min(100, len(x_test))
                        x_subset = x_test[:max_samples]
                        y_subset = y_test[:max_samples]
                        
                        poisoned_data, poisoned_labels = attack.poison(x_subset, y_subset)
                        success_rate = np.mean(
                            np.argmax(poisoned_labels, axis=1) != np.argmax(y_subset, axis=1)
                        )
                
                results.append({
                    "type": "warning" if success_rate < 0.5 else "error",
                    "name": name,
                    "description": f"Model vulnerable to {name} attack (success rate: {success_rate*100:.1f}%)",
                    "severity": "MEDIUM" if success_rate < 0.5 else "HIGH",
                    "attack_type": attack_type,
                    "success_rate": float(success_rate)
                })
            except Exception as e:
                logger.error(f"Attack {name} failed: {str(e)}")
                results.append({
                    "type": "error",
                    "name": name,
                    "description": f"Attack failed: {str(e)}",
                    "severity": "ERROR",
                    "attack_type": attack_type,
                    "success_rate": 0.0
                })
        return results

    def scan_model(self, x_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Run comprehensive adversarial testing."""
        try:
            scan_start = datetime.now()
            
            # Get applicable attack types
            attacks = self._get_applicable_attacks()
            
            # Track test counts
            test_details = {
                'evasion_tests': len(attacks.get('evasion', {})),
                'extraction_tests': len(attacks.get('extraction', {})),
                'poisoning_tests': len(attacks.get('poisoning', {})) if not self.is_blackbox else 0,
                'completed_tests': 0,
                'failed_tests': 0
            }
            
            # Run different types of attacks
            all_results = []
            for attack_type in attacks.keys():
                results = self.run_attacks(attack_type, x_test, y_test)
                all_results.extend(results)
            
            # Update test counts
            test_details['completed_tests'] = len(all_results)
            test_details['failed_tests'] = len([r for r in all_results if r['type'] == 'error'])
            
            scan_end = datetime.now()
            
            return {
                "module": "AdversarialTesting",
                "file": str(self.classifier.model_file) if hasattr(self.classifier, 'model_file') else None,
                "endpoint": str(self.classifier.endpoint_url) if hasattr(self.classifier, 'endpoint_url') else None,
                "status": "unsafe" if any(r["type"] == "error" for r in all_results) else "safe",
                "issues": all_results,
                "metadata": {
                    "scan_time": str(scan_end - scan_start),
                    "target": "file" if not self.is_blackbox else "endpoint",
                    "framework": self.framework,
                    "test_samples": len(x_test),
                    "test_details": test_details,
                    "summary": f"Found {len(all_results)} issues in {test_details['completed_tests']} tests"
                }
            }
            
        except Exception as e:
            return {
                "module": "AdversarialTesting",
                "file": None,
                "endpoint": None,
                "status": "error",
                "issues": [{
                    "type": "error",
                    "description": str(e),
                    "severity": "CRITICAL",
                    "attack_type": "unknown"
                }],
                "metadata": {
                    "scan_time": "N/A",
                    "target": "unknown",
                    "framework": self.framework,
                    "test_details": {
                        "evasion_tests": 0,
                        "extraction_tests": 0,
                        "poisoning_tests": 0,
                        "completed_tests": 0,
                        "failed_tests": 1
                    },
                    "summary": f"Scan failed: {str(e)}"
                }
            }
