import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from src import main

class TestMain(unittest.TestCase):
    def test_has_keywords(self):
        # Should match keywords in title or description
        self.assertTrue(main.has_keywords("Python developer", ""))
        self.assertTrue(main.has_keywords("", "React.js experience required"))
        self.assertTrue(main.has_keywords("AWS cloud skills", ""))
        self.assertTrue(main.has_keywords("", "NodeJS engineer"))
        self.assertTrue(main.has_keywords("Django dev", "Flask dev"))
        # Should not match
        self.assertFalse(main.has_keywords("Marketing manager", ""))
        self.assertFalse(main.has_keywords("", "Sales position"))
        self.assertFalse(main.has_keywords("Office administrator", ""))

    @patch("src.main.requests.get")
    @patch("src.main.is_new_job", return_value=True)
    def test_list_relevant_jobs_success(self, mock_is_new_job, mock_get):
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
    @patch("src.main.is_new_job", return_value=True)
    def test_list_relevant_jobs_failure(self, mock_is_new_job, mock_get):
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

    @patch("src.main.boto3.resource")
    def test_is_new_job_true(self, mock_boto_resource):
        # Simulate DynamoDB returning no item (new job)
        mock_table = MagicMock()
        mock_table.get_item.return_value = {}
        mock_boto_resource.return_value.Table.return_value = mock_table
        self.assertTrue(main.is_new_job("python developer", "2024-01-01"))

    @patch("src.main.boto3.resource")
    def test_is_new_job_false(self, mock_boto_resource):
        # Simulate DynamoDB returning an item (not new)
        mock_table = MagicMock()
        mock_table.get_item.return_value = {"Item": {"title": "python developer", "isoDate": "2024-01-01"}}
        mock_boto_resource.return_value.Table.return_value = mock_table
        self.assertFalse(main.is_new_job("python developer", "2024-01-01"))

if __name__ == "__main__":
    unittest.main()
