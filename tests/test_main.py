import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from src import main

class TestMain(unittest.TestCase):
    def test_has_keywords(self):
        self.assertTrue(main.has_keywords("Python developer needed"))
        self.assertTrue(main.has_keywords("Looking for React.js skills"))
        self.assertFalse(main.has_keywords("Marketing manager"))

    @patch("src.main.requests.get")
    def test_list_relevant_jobs_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jobs": [
                {"title": "Python Developer", "description": "Work with Django", "url": "http://example.com", "isoDate": "2024-01-01"},
                {"title": "Marketing", "description": "Not relevant", "url": "http://example.com", "isoDate": "2024-01-01"}
            ]
        }
        mock_get.return_value = mock_response
        jobs = main.list_relevant_jobs("Software Engineer", "Remote")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "python developer")

    @patch("src.main.requests.get")
    def test_list_relevant_jobs_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        jobs = main.list_relevant_jobs("Software Engineer", "Remote")
        self.assertEqual(jobs, [])

    @patch("src.main.boto3.client")
    def test_email_jobs_success(self, mock_boto_client):
        mock_ses = MagicMock()
        mock_boto_client.return_value = mock_ses
        mock_ses.send_email.return_value = {"MessageId": "test-id"}
        jobs = [{"title": "python developer", "description": "", "url": "http://example.com", "date": "2024-01-01"}]
        # Should not raise
        main.sender_email_address = "test@sender.com"
        main.receiver_email_address = "test@receiver.com"
        main.email_jobs(jobs)
        mock_ses.send_email.assert_called_once()

    @patch("src.main.boto3.client")
    def test_email_jobs_failure(self, mock_boto_client):
        mock_ses = MagicMock()
        mock_boto_client.return_value = mock_ses
        error_response = {"Error": {"Code": "MockError", "Message": "fail"}}
        mock_ses.send_email.side_effect = ClientError(error_response, "SendEmail")
        jobs = [{"title": "python developer", "description": "", "url": "http://example.com", "date": "2024-01-01"}]
        main.sender_email_address = "test@sender.com"
        main.receiver_email_address = "test@receiver.com"
        try:
            main.email_jobs(jobs)
        except Exception:
            self.fail("email_jobs raised Exception unexpectedly!")

if __name__ == "__main__":
    unittest.main()
