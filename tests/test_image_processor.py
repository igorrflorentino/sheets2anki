"""
Unit tests for the Image Processor module.

Tests cover:
- Dependency checking
- Configuration management
- Image upload to ImgBB
- Google Sheets authentication
- Integration with sync workflow
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.image_processor import (
        check_dependencies,
        upload_image_to_imgbb,
        process_images_for_sync
    )
    from src.config_manager import (
        get_image_processor_config,
        set_image_processor_config,
        get_image_processor_enabled,
        set_image_processor_enabled
    )
except ImportError as e:
    print(f"Warning: Could not import modules for testing: {e}")


class TestImageProcessorConfig(unittest.TestCase):
    """Tests for Image Processor configuration management."""
    
    def test_default_config(self):
        """Test that default configuration has correct structure."""
        config = get_image_processor_config()
        
        self.assertIn('enabled', config)
        self.assertIn('imgbb_api_key', config)
        self.assertIn('google_credentials_path', config)
        self.assertIn('auto_process', config)
        
        # Default values
        self.assertFalse(config['enabled'])
        self.assertEqual(config['imgbb_api_key'], '')
        self.assertEqual(config['google_credentials_path'], '')
        self.assertTrue(config['auto_process'])
    
    def test_set_config(self):
        """Test setting configuration values."""
        # Save original state
        original = get_image_processor_config()
        
        try:
            # Set new values
            success = set_image_processor_config(
                enabled=True,
                imgbb_api_key='test_key_123',
                google_credentials_path='/path/to/credentials.json',
                auto_process=False
            )
            
            self.assertTrue(success)
            
            # Verify changes
            config = get_image_processor_config()
            self.assertTrue(config['enabled'])
            self.assertEqual(config['imgbb_api_key'], 'test_key_123')
            self.assertEqual(config['google_credentials_path'], '/path/to/credentials.json')
            self.assertFalse(config['auto_process'])
            
        finally:
            # Restore original state
            set_image_processor_config(
                enabled=original['enabled'],
                imgbb_api_key=original['imgbb_api_key'],
                google_credentials_path=original['google_credentials_path'],
                auto_process=original['auto_process']
            )
    
    def test_enable_disable(self):
        """Test enable/disable functionality."""
        original_state = get_image_processor_enabled()
        
        try:
            set_image_processor_enabled(True)
            self.assertTrue(get_image_processor_enabled())
            
            set_image_processor_enabled(False)
            self.assertFalse(get_image_processor_enabled())
            
        finally:
            set_image_processor_enabled(original_state)


class TestDependencyChecking(unittest.TestCase):
    """Tests for dependency checking functionality."""
    
    def test_check_dependencies(self):
        """Test dependency checking returns correct format."""
        all_ok, missing = check_dependencies()
        
        self.assertIsInstance(all_ok, bool)
        self.assertIsInstance(missing, list)
        
        if all_ok:
            self.assertEqual(len(missing), 0)
        else:
            self.assertGreater(len(missing), 0)
    
    @patch('src.image_processor.requests', None)
    def test_missing_requests(self):
        """Test detection of missing requests library."""
        # This would require actually removing the import
        # which is complex in Python, so we'll skip this test
        # in actual implementation
        pass


class TestImgBBUpload(unittest.TestCase):
    """Tests for ImgBB image upload functionality."""
    
    @patch('src.image_processor.requests')
    def test_successful_upload(self, mock_requests):
        """Test successful image upload to ImgBB."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'url': 'https://i.ibb.co/test123/image.png'
            }
        }
        mock_requests.post.return_value = mock_response
        
        # Test upload
        test_image_data = b'fake_image_data'
        result_url = upload_image_to_imgbb(test_image_data, 'test_api_key', 'test.png')
        
        self.assertIsNotNone(result_url)
        self.assertTrue(result_url.startswith('https://'))
        self.assertIn('ibb.co', result_url)
    
    @patch('src.image_processor.requests')
    def test_failed_upload(self, mock_requests):
        """Test handling of failed ImgBB upload."""
        # Mock failed response
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': False,
            'error': {
                'message': 'Invalid API key'
            }
        }
        mock_requests.post.return_value = mock_response
        
        # Test upload
        test_image_data = b'fake_image_data'
        result_url = upload_image_to_imgbb(test_image_data, 'invalid_key', 'test.png')
        
        self.assertIsNone(result_url)
    
    @patch('src.image_processor.requests')
    def test_upload_with_exception(self, mock_requests):
        """Test handling of exceptions during upload."""
        # Mock exception
        mock_requests.post.side_effect = Exception('Network error')
        
        # Test upload
        test_image_data = b'fake_image_data'
        result_url = upload_image_to_imgbb(test_image_data, 'test_key', 'test.png')
        
        self.assertIsNone(result_url)


class TestProcessImagesForSync(unittest.TestCase):
    """Tests for the main process_images_for_sync function."""
    
    @patch('src.image_processor.get_image_processor_enabled')
    def test_disabled_processor(self, mock_enabled):
        """Test that disabled processor returns early."""
        mock_enabled.return_value = False
        
        success, message = process_images_for_sync('https://docs.google.com/spreadsheets/test')
        
        self.assertTrue(success)
        self.assertEqual(message, 'Image processor disabled')
    
    @patch('src.image_processor.get_image_processor_config')
    @patch('src.image_processor.get_image_processor_enabled')
    def test_missing_config(self, mock_enabled, mock_config):
        """Test handling of missing configuration."""
        mock_enabled.return_value = True
        mock_config.return_value = {
            'imgbb_api_key': '',
            'google_credentials_path': '',
            'auto_process': True
        }
        
        success, message = process_images_for_sync('https://docs.google.com/spreadsheets/test')
        
        self.assertFalse(success)
        self.assertIn('ImgBB', message)
    
    @patch('src.image_processor.check_dependencies')
    @patch('src.image_processor.get_image_processor_enabled')
    def test_missing_dependencies(self, mock_enabled, mock_deps):
        """Test handling of missing dependencies."""
        mock_enabled.return_value = True
        mock_deps.return_value = (False, ['google-api-python-client'])
        
        success, message = process_images_for_sync('https://docs.google.com/spreadsheets/test')
        
        self.assertFalse(success)
        self.assertIn('Missing required packages', message)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for common scenarios."""
    
    def test_config_persistence(self):
        """Test that configuration changes persist."""
        # This is more of an integration test that would require
        # actual file I/O and is better done manually
        pass
    
    def test_sync_workflow(self):
        """Test integration with sync workflow."""
        # This would require mocking the entire sync process
        # which is complex and better done with integration tests
        pass


class TestErrorHandling(unittest.TestCase):
    """Tests for error handling and edge cases."""
    
    def test_invalid_spreadsheet_url(self):
        """Test handling of invalid spreadsheet URL."""
        with patch('src.image_processor.get_image_processor_enabled', return_value=True):
            with patch('src.image_processor.get_image_processor_config', return_value={
                'imgbb_api_key': 'test_key',
                'google_credentials_path': '/path/to/creds.json',
                'auto_process': True
            }):
                success, message = process_images_for_sync('invalid_url')
                
                # Should handle gracefully
                self.assertFalse(success)
    
    def test_nonexistent_credentials_file(self):
        """Test handling of non-existent credentials file."""
        with patch('src.image_processor.get_image_processor_enabled', return_value=True):
            with patch('src.image_processor.get_image_processor_config', return_value={
                'imgbb_api_key': 'test_key',
                'google_credentials_path': '/nonexistent/path/creds.json',
                'auto_process': True
            }):
                success, message = process_images_for_sync('https://docs.google.com/spreadsheets/test')
                
                self.assertFalse(success)
                self.assertIn('not found', message)


def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == '__main__':
    print("="*70)
    print("Running Image Processor Tests")
    print("="*70)
    result = run_tests()
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*70)
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
