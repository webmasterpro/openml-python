__author__ = 'feurerm'

import unittest
import os
import shutil
import sys

if sys.version_info[0] >= 3:
    from unittest import mock
else:
    import mock

from openml.util import is_string

from openml.apiconnector import APIConnector
from openml.entities.dataset import OpenMLDataset
from openml.entities.split import OpenMLSplit


class TestAPIConnector(unittest.TestCase):
    """Test the APIConnector

    Note
    ----
    A config file with the username and password must be present to test the
    API calls.
    """

    def setUp(self):
        self.cwd = os.getcwd()
        workdir = os.path.dirname(os.path.abspath(__file__))
        self.workdir = os.path.join(workdir, "tmp")
        try:
            shutil.rmtree(self.workdir)
        except:
            pass

        os.mkdir(self.workdir)
        os.chdir(self.workdir)

        self.cached = True
        self.connector = APIConnector(cache_directory=self.workdir)
        print(self.connector._session_hash)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.workdir)

    ############################################################################
    # Test administrative stuff
    @mock.patch.object(APIConnector, '_perform_api_call', autospec=True)
    def test_authentication(self, mock_perform_API_call):
        # TODO return error messages
        mock_perform_API_call.return_value = 400, \
        """ <oml:authenticate xmlns:oml = "http://openml.org/openml">
            <oml:session_hash>G9MPPN114ZCZNWW2VN3JE9VF1FMV8Y5FXHUDUL4P</oml:session_hash>
            <oml:valid_until>2017-08-13 20:01:29</oml:valid_until>
            <oml:timezone>Europe/Berlin</oml:timezone>
            </oml:authenticate> """

        # This already does an authentication
        connector = APIConnector()
        # but we only test it here...
        self.assertEqual(1, mock_perform_API_call.call_count)
        self.assertEqual(connector._session_hash,
                         "G9MPPN114ZCZNWW2VN3JE9VF1FMV8Y5FXHUDUL4P")

        # Test that it actually returns what we want
        session_hash = connector._authenticate("Bla", "Blub")
        self.assertEqual(2, mock_perform_API_call.call_count)
        self.assertEqual(session_hash,
                         "G9MPPN114ZCZNWW2VN3JE9VF1FMV8Y5FXHUDUL4P")

    @unittest.skip("Not implemented yet.")
    def test_parse_config(self):
        raise Exception()

    ############################################################################
    # Test all local stuff
    def test_get_cached_datasets(self):
        workdir = os.path.dirname(os.path.abspath(__file__))
        workdir = os.path.join(workdir, "files")
        connector = APIConnector(cache_directory=workdir)
        datasets = connector.get_cached_datasets()
        self.assertIsInstance(datasets, dict)
        self.assertEqual(len(datasets), 2)
        self.assertIsInstance(datasets.values()[0], OpenMLDataset)

    def test_get_cached_dataset(self):
        workdir = os.path.dirname(os.path.abspath(__file__))
        workdir = os.path.join(workdir, "files")

        with mock.patch.object(APIConnector, "_perform_api_call") as api_mock:
            api_mock.return_value = 400, \
                """<oml:authenticate xmlns:oml = "http://openml.org/openml">
                <oml:session_hash>G9MPPN114ZCZNWW2VN3JE9VF1FMV8Y5FXHUDUL4P</oml:session_hash>
                <oml:valid_until>2014-08-13 20:01:29</oml:valid_until>
                <oml:timezone>Europe/Berlin</oml:timezone>
                </oml:authenticate>"""

            connector = APIConnector(cache_directory=workdir)
            dataset = connector.get_cached_dataset(2)
            self.assertIsInstance(dataset, OpenMLDataset)
            self.assertTrue(connector._perform_api_call.is_called_once())

    def test_get_chached_dataset_description(self):
        workdir = os.path.dirname(os.path.abspath(__file__))
        workdir = os.path.join(workdir, "files")
        connector = APIConnector(cache_directory=workdir)
        description = connector._get_cached_dataset_description(2)
        self.assertIsInstance(description, dict)

    @unittest.skip("Not implemented yet.")
    def test_get_cached_tasks(self):
        raise Exception()

    @unittest.skip("Not implemented yet.")
    def test_get_cached_task(self):
        raise Exception()

    @unittest.skip("Not implemented yet.")
    def test_get_cached_splits(self):
        raise Exception()

    @unittest.skip("Not implemented yet.")
    def test_get_cached_split(self):
        raise Exception()

    ############################################################################
    # Test all remote stuff

    ############################################################################
    # Datasets
    def test_get_dataset_list(self):
        # We can only perform a smoke test here because we test on dynamic
        # data from the internet...
        datasets = self.connector.get_dataset_list()
        # 1087 as the number of datasets on openml.org
        self.assertTrue(len(datasets) >= 1087)
        for dataset in datasets:
            self.assertEqual(type(dataset), dict)
            self.assertGreaterEqual(len(dataset), 2)
            self.assertIn('did', dataset)
            self.assertIsInstance(dataset['did'], int)
            self.assertIn('status', dataset)
            self.assertTrue(is_string(dataset['status']))
            self.assertIn(dataset['status'], ['in_preparation', 'active',
                                              'deactivated'])

    @unittest.skip("Not implemented yet.")
    def test_datasets_active(self):
        raise NotImplementedError()

    def test_download_datasets(self):
        dids = [1, 2]
        datasets = self.connector.download_datasets(dids)
        self.assertEqual(len(datasets), 2)
        self.assertTrue(os.path.exists(os.path.join(
            self.connector.dataset_cache_dir, "1", "description.xml")))
        self.assertTrue(os.path.exists(os.path.join(
            self.connector.dataset_cache_dir, "2", "description.xml")))
        self.assertTrue(os.path.exists(os.path.join(
            self.connector.dataset_cache_dir, "1", "dataset.arff")))
        self.assertTrue(os.path.exists(os.path.join(
            self.connector.dataset_cache_dir, "2", "dataset.arff")))

    def test_download_dataset(self):
        dataset = self.connector.download_dataset(1)
        self.assertEqual(type(dataset), OpenMLDataset)
        self.assertEqual(dataset.name, 'anneal')
        self.assertTrue(os.path.exists(os.path.join(
            self.connector.dataset_cache_dir, "1", "description.xml")))
        self.assertTrue(os.path.exists(os.path.join(
            self.connector.dataset_cache_dir, "1", "dataset.arff")))

    def test_download_rowid(self):
        # Smoke test which checks that the dataset has the row-id set correctly
        did = 164
        dataset = self.connector.download_dataset(did)
        self.assertEqual(dataset.row_id_attribute, 'instance')

    def test_download_dataset_description(self):
        # Only a smoke test, I don't know exactly how to test the URL
        # retrieval and "caching"
        description = self.connector.download_dataset_description(2)
        self.assertIsInstance(description, dict)

    def test_download_dataset_features(self):
        # Only a smoke check
        features = self.connector.download_dataset_features(2)
        self.assertIsInstance(features, dict)

    def test_download_dataset_qualities(self):
        # Only a smoke check
        qualities = self.connector.download_dataset_qualities(2)
        self.assertIsInstance(qualities, dict)

    ############################################################################
    # Tasks
    def test_get_task_list(self):
        # We can only perform a smoke test here because we test on dynamic
        # data from the internet...
        def check_task(task):
            self.assertEqual(type(task), dict)
            self.assertGreaterEqual(len(task), 2)
            self.assertIn('did', task)
            self.assertIsInstance(task['did'], int)
            self.assertIn('status', task)
            self.assertTrue(is_string(task['status']))
            self.assertIn(task['status'],
                          ['in_preparation', 'active', 'deactivated'])

        tasks = self.connector.get_task_list(task_type_id=1)
        # 1759 as the number of supervised classification tasks retrieved
        # openml.org from this call; don't trust the number on openml.org as
        # it also counts private datasets
        self.assertGreaterEqual(len(tasks), 1759)
        for task in tasks:
            check_task(task)

        tasks = self.connector.get_task_list(task_type_id=2)
        self.assertGreaterEqual(len(tasks), 735)
        for task in tasks:
            check_task(task)

    def test_download_task(self):
        task = self.connector.download_task(1)
        self.assertTrue(os.path.exists(
            os.path.join(os.getcwd(), "tasks", "1", "task.xml")))
        self.assertTrue(os.path.exists(
            os.path.join(os.getcwd(), "tasks", "1", "datasplits.arff")))
        self.assertTrue(os.path.exists(
            os.path.join(os.getcwd(), "datasets", "1", "dataset.arff")))

    def test_download_split(self):
        task = self.connector.download_task(1)
        split = self.connector.download_split(task)
        self.assertEqual(type(split), OpenMLSplit)
        self.assertTrue(os.path.exists(
            os.path.join(os.getcwd(), "tasks", "1", "datasplits.arff")))

    def test_upload_dataset(self):

        dataset = """@relation accelerometer

                     @attribute id {?}
                     @attribute bag relational
                        @attribute y numeric
                        @attribute x numeric
                        @attribute z numeric
                    @end bag

                    @attribute class {A,B,C,?}

                    @data
                    ?,"3.18163375854,-1.96720916748,9.26677963257\n3.52741470337,-2.7294241333,9.70147567749\n
                    4.42030792236,-0.964743804932,6.52074005127\n
                    4.59963500977,-2.74214767456,8.6741619873\n5.19749176025,-1.80330001831,7.57110580444\n","?"
                    """
        description = """ <oml:data_set_description xmlns:oml="http://openml.org/openml">
                        <oml:name>anneal</oml:name>
                        <oml:version>1</oml:version>
                        <oml:description>test</oml:description>
                        <oml:format>ARFF</oml:format>
                        <oml:upload_date>2014-04-06 23:19:24</oml:upload_date>
                        <oml:licence>Public</oml:licence>
                        <oml:url></oml:url>
                        <oml:default_target_attribute>class</oml:default_target_attribute>
                        <oml:md5_checksum></oml:md5_checksum>
                        </oml:data_set_description>
                         """
        return_code, dataset_xml = self.connector.upload_dataset(dataset, description)
        self.assertEqual(return_code, 200)

    def test_upload_dataset_features(self):
        raise Exception()

    def test_upload_dataset_qualities(self):

        description = """ <oml:data_qualities xmlns:oml="http://openml.org/openml">
                          <oml:did>1</oml:did>
                          <oml:quality>
                            <oml:name>NumberOfInstances</oml:name>
                            <oml:value>898</oml:value>
                          </oml:quality>
                          </oml:data_qualities>
                        """
        return_code, dataset_xml = self.connector.upload_dataset_qualities(description)
        self.assertEqual(return_code, 200)




