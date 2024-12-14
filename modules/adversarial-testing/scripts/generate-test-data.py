import argparse
import numpy as np
import os
from typing import Tuple, Dict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestDataGenerator:
    """Generate synthetic test data for different ML frameworks."""
    
    @staticmethod
    def create_image_data(samples: int, shape: Tuple[int, ...]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create synthetic image data.
        
        Args:
            samples: Number of samples to generate
            shape: Shape of each sample (height, width, channels)
            
        Returns:
            Tuple of (x_data, y_data)
        """
        x_data = np.random.random((samples, *shape))
        y_data = np.eye(10)[np.random.randint(0, 10, samples)]  # 10-class classification
        return x_data, y_data
        
    @staticmethod
    def create_tabular_data(samples: int, features: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create synthetic tabular data.
        
        Args:
            samples: Number of samples to generate
            features: Number of features per sample
            
        Returns:
            Tuple of (x_data, y_data)
        """
        x_data = np.random.random((samples, features))
        y_data = np.eye(2)[np.random.randint(0, 2, samples)]  # Binary classification
        return x_data, y_data

    def generate_data(
        self,
        framework: str,
        samples: int,
        data_type: str = 'image'
    ) -> Dict[str, np.ndarray]:
        """
        Generate framework-specific test data.
        
        Args:
            framework: ML framework ('tensorflow', 'pytorch', 'sklearn')
            samples: Number of samples to generate
            data_type: Type of data to generate ('image' or 'tabular')
            
        Returns:
            Dict containing x_test and y_test arrays
        """
        try:
            if data_type == 'image':
                if framework == 'tensorflow':
                    # TensorFlow expects (batch, height, width, channels)
                    x_test, y_test = self.create_image_data(samples, (28, 28, 1))
                elif framework == 'pytorch':
                    # PyTorch expects (batch, channels, height, width)
                    x_test, y_test = self.create_image_data(samples, (1, 28, 28))
                else:  # sklearn
                    # Flatten images for sklearn
                    x_test, y_test = self.create_image_data(samples, (28, 28, 1))
                    x_test = x_test.reshape(samples, -1)
            else:  # tabular
                x_test, y_test = self.create_tabular_data(samples, features=20)
                
            return {
                'x_test': x_test.astype(np.float32),
                'y_test': y_test.astype(np.float32)
            }
            
        except Exception as e:
            logger.error(f"Error generating test data: {str(e)}")
            raise

def setup_argparser() -> argparse.ArgumentParser:
    """Configure command line argument parser."""
    parser = argparse.ArgumentParser(
        description='Generate test data for adversarial testing',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--format',
        choices=['tensorflow', 'pytorch', 'sklearn'],
        required=True,
        help='ML framework format'
    )
    
    parser.add_argument(
        '--samples',
        type=int,
        default=1000,
        help='Number of test samples to generate'
    )
    
    parser.add_argument(
        '--output',
        default='test_samples.npz',
        help='Output file path'
    )
    
    parser.add_argument(
        '--type',
        choices=['image', 'tabular'],
        default='image',
        help='Type of data to generate'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser

def main():
    """Main entry point for test data generation."""
    parser = setup_argparser()
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        logger.info(f"Generating {args.samples} {args.type} samples for {args.format}")
        
        # Create generator and generate data
        generator = TestDataGenerator()
        data = generator.generate_data(
            framework=args.format,
            samples=args.samples,
            data_type=args.type
        )
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
        
        # Save the data
        np.savez(args.output, **data)
        
        logger.info(f"Successfully saved test data to {args.output}")
        logger.info(f"Data shapes: x_test: {data['x_test'].shape}, y_test: {data['y_test'].shape}")
        
    except Exception as e:
        logger.error(f"Failed to generate test data: {str(e)}")
        raise

if __name__ == '__main__':
    main()
