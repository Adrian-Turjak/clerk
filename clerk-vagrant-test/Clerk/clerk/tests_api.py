from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from clerk.tests import create_date


def compare_data(testCase, data, data2, fields):
    """Helper function to save on code repetition for compares."""
    for key in fields:
        testCase.assertEqual(data[key], data2[key])


def login_client(testcase):
    User.objects.create_superuser(username='lauren', password='secret',
                                  email='')
    testcase.login(username='lauren', password='secret')


def create_region_and_services(testcase, servName, locName, rate):
    data = {'name': servName, 'pretty_name': servName,
            'description': 'this is a service type'}
    testcase.client.post('/service_types/', data, format='json')
    data = {'name': locName, 'description': 'this is a region',
            'serv1_rate': rate}
    return testcase.client.post('/regions/', data, format='json')


class Service_Type_List_Tests(APITestCase):

    def test_post_service_type_list(self):
        """Checks that you can create a service_type"""
        login_client(self.client)
        data = {'name': 'serv1', 'pretty_name': 'Service 1',
                'description': 'this is a service type'}
        response = self.client.post('/service_types/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_service_type_list_fail_1(self):
        """Checks that you can't create two service types with
           the same name."""
        login_client(self.client)
        data = {'name': 'serv1', 'pretty_name': 'Service 1',
                'description': 'this is a service type'}
        self.client.post('/service_types/', data, format='json')
        data = {'name': 'serv1', 'pretty_name': 'Service 1',
                'description': 'this is a service type'}
        response = self.client.post('/service_types/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_service_type_list_fail_2(self):
        """Checks for bad request on missing or wrong parameters."""
        login_client(self.client)
        # wrong formats: space in name
        data = {'name': 'serv 1', 'pretty_name': 'Service 1',
                'description': 'this is a service type'}
        response = self.client.post('/service_types/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # missing parameter
        data = {'name': 'serv1', 'description': 'this is a service type'}
        response = self.client.post('/service_types/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_service_type_permission_denied(self):
        data = {'name': 'serv 1', 'pretty_name': 'Service 1',
                'description': 'this is a service type'}
        response = self.client.post('/service_types/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_service_type_list(self):
        """"""
        login_client(self.client)
        services = []
        for i in range(10):
            data = {'name': 'serv' + str(i),
                    'pretty_name': 'Service ' + str(i),
                    'description': 'this is a service type'}
            services.append(data)
            self.client.post('/service_types/', data, format='json')

        service_types = self.client.get('/service_types/').data

        for service in service_types:
            # deletes the created key to make comparison easier
            del service['created']
            self.assertTrue(services.__contains__(service))


class Service_Type_Detail_Tests(APITestCase):

    def test_put_service_type_detail(self):
        """Test that you can override another service_type"""
        login_client(self.client)
        data = {'name': 'serv1', 'pretty_name': 'Service 1',
                'description': 'this is a service type'}
        self.client.post('/service_types/', data, format='json')
        data = {'name': 'serv6', 'pretty_name': 'Service 6',
                'description': 'this is a service type'}
        response = self.client.put('/service_types/serv1/',
                                   data, format='json')
        compare_data(self, response.data, data, ['name', 'pretty_name',
                                                 'description'])

    def test_put_service_type_detail_fail_1(self):
        """Checks that it can't put without all parameters."""
        login_client(self.client)
        data = {'name': 'serv1', 'pretty_name': 'Service 1',
                'description': 'this is a service type'}
        self.client.post('/service_types/', data, format='json')
        data = {'name': 'serv6', 'pretty_name': 'Service 6'}
        response = self.client.put('/service_types/serv1/',
                                   data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_service_type_detail_fail_2(self):
        """Tests that you can't rename a service type
           to another existing one."""
        login_client(self.client)
        data = {'name': 'serv1', 'pretty_name': 'Service 1',
                'description': 'this is a service type'}
        self.client.post('/service_types/', data, format='json')
        data = {'name': 'serv6', 'pretty_name': 'Service 6',
                'description': 'this is a service type'}
        self.client.post('/service_types/', data, format='json')
        data = {'name': 'serv6', 'pretty_name': 'Service 6',
                'description': 'this is a service type'}
        response = self.client.put('/service_types/serv1/',
                                   data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_service_type_detail_fail_3(self):
        """Checks that it can't put if service type doesn't exist."""
        login_client(self.client)
        data = {'name': 'serv6', 'pretty_name': 'Service 6'}
        response = self.client.put('/service_types/serv1/',
                                   data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_puth_service_type_detail_permission_denied(self):
        """Checks that it can't put if not logged in."""
        data = {'name': 'serv6', 'pretty_name': 'Service 6'}
        response = self.client.patch('/service_types/serv1/',
                                     data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_service_type_detail(self):
        """Ensures you can patch a service_type"""
        login_client(self.client)
        data = {'name': 'serv1', 'pretty_name': 'Service 1',
                'description': 'this is a service type'}
        self.client.post('/service_types/', data, format='json')
        data = {'name': 'serv6', 'pretty_name': 'Service 6'}
        response = self.client.patch('/service_types/serv1/',
                                     data, format='json')
        compare_data(self, response.data, data, ['name', 'pretty_name'])

    def test_patch_service_type_detail_fail(self):
        """Checks that it can't patch if service type doesn't exist."""
        login_client(self.client)
        data = {'name': 'serv6', 'pretty_name': 'Service 6'}
        response = self.client.patch('/service_types/serv1/',
                                     data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_service_type_detail_permission_denied(self):
        """Checks that it can't patch if not logged in."""
        data = {'name': 'serv6', 'pretty_name': 'Service 6'}
        response = self.client.patch('/service_types/serv1/',
                                     data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_service_type_detail_permission_denied(self):
        """Checks that it can't delete."""
        login_client(self.client)
        response = self.client.delete('/service_types/serv1/')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class Region_List_Tests(APITestCase):

    def test_post_regions_list(self):
        """Tests that you are able to create new regions
           with no service_types present."""
        login_client(self.client)
        data = {'name': 'loc1', 'description': 'this is a region'}
        response = self.client.post('/regions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        compare_data(self, response.data, data, ['name', 'description'])

    def test_post_regions_list_1(self):
        """Tests that you are able to create new regions
           with service_types present."""
        login_client(self.client)
        data = {'name': 'serv1', 'pretty_name': 'Service 1',
                'description': 'this is a service type'}
        response = self.client.post('/service_types/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Because there is a service_type, a rate has to be given.
        data = {'name': 'loc1', 'description': 'this is a region',
                'serv1_rate': '5'}
        response = self.client.post('/regions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        compare_data(self, response.data, data, ['name', 'description'])

    def test_post_regions_list_2(self):
        """Tests that the service created along with region
           does create the correct given rate.
           - Here we assume get works for rates
                   (provided those tests pass)"""
        login_client(self.client)
        create_region_and_services(self, 'serv1', 'loc1', 5)
        response = self.client.get('/regions/loc1/services/serv1/' +
                                   'rates/current/')
        self.assertEqual(response.data['rate'], 5)

    def test_post_regions_list_fail_1(self):
        """Should return a bad request if trying to create a new
           region with the same name"""
        login_client(self.client)
        data = {'name': 'loc1', 'description': 'this is a region'}
        self.client.post('/regions/', data, format='json')
        response = self.client.post('/regions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_regions_list_fail_2(self):
        """Should return a bad request if missing required
           parameters, or in wrong format."""
        login_client(self.client)
        data = {'name': 'serv1', 'pretty_name': 'Service 1',
                'description': 'this is a service type'}
        self.client.post('/service_types/', data, format='json')

        # Missing parameters:
        data = {}
        response = self.client.post('/regions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {'name': 'loc1'}
        response = self.client.post('/regions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {'description': 'stuff'}
        response = self.client.post('/regions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {'name': 'loc1', 'description': 'this is a region'}
        response = self.client.post('/regions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # wrong formats sent:  spaces in name
        data = {'name': 'loc 1', 'description': 'this is a region',
                'rate': '5'}
        response = self.client.post('/regions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
         # wrong formats sent:  text as rate
        data = {'name': 'loc 1', 'description': 'this is a region',
                'rate': 'words'}
        response = self.client.post('/regions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_regions_list_permission_denied(self):
        """Should deny post request if not logged in."""
        data = {'name': 'loc1', 'description': 'this is a region'}
        response = self.client.post('/regions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_regions_list(self):
        """Makes sure all existing regions are being returned."""
        login_client(self.client)
        regions = []
        for i in range(20):
            data = {'name': 'loc' + str(i),
                    'description': 'description' + str(i)}
            regions.append(data)
            self.client.post('/regions/', data, format='json')
        response = self.client.get('/regions/')
        for i in range(20):
            compare_data(self, response.data[1], regions[1],
                         ['name', 'description'])


class Region_Detail_Tests(APITestCase):

    def test_put_region_detail(self):
        """Checks that you are able to override existing regions."""
        login_client(self.client)
        data = {'name': 'loc1', 'description': 'this is a region'}
        self.client.post('/regions/', data, format='json')
        data = {'name': 'loc2', 'description': 'this is a region'}
        response = self.client.put('/regions/loc1/', data, format='json')
        compare_data(self, response.data, data, ['name', 'description'])

    def test_put_region_detail_fail(self):
        """Check to ensure not found is returned if no region exists."""
        login_client(self.client)
        data = {'name': 'loc2', 'description': 'this is a region'}
        response = self.client.put('/regions/loc1/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_region_detail_fail_2(self):
        """Check to ensure you cannot rename a region to another
           existing region. If this test passes,
           the same is ensured for patch."""
        login_client(self.client)
        data = {'name': 'loc1', 'description': 'this is a region'}
        self.client.post('/regions/', data, format='json')
        data = {'name': 'loc2', 'description': 'this is a region'}
        self.client.post('/regions/', data, format='json')
        data = {'name': 'loc2', 'description': 'this is a region'}
        response = self.client.put('/regions/loc1/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_regions_detail_permission_denied(self):
        """Should deny put request if not logged in."""
        data = {'name': 'loc1', 'description': 'this is a region'}
        response = self.client.put('/regions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_region_detail(self):
        """Checks that you are able to patch existing regions."""
        login_client(self.client)
        data = {'name': 'loc1', 'description': 'this is a region'}
        self.client.post('/regions/', data, format='json')
        data = {'name': 'loc2'}
        response = self.client.patch('/regions/loc1/', data, format='json')
        compare_data(self, response.data, data, ['name'])

    def test_patch_region_detail_fail(self):
        """Check to ensure not found is returned if no region exists."""
        login_client(self.client)
        data = {'name': 'loc2', 'description': 'this is a region'}
        response = self.client.patch('/regions/loc1/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_regions_detail_permission_denied(self):
        """Should deny put request if not logged in."""
        data = {'name': 'loc1', 'description': 'this is a region'}
        response = self.client.patch('/regions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_region_detail(self):
        """Makes sure all existing regions can be returned."""
        login_client(self.client)
        for i in range(20):
            data = {'name': 'loc' + str(i),
                    'description': 'description' + str(i)}
            self.client.post('/regions/', data, format='json')
        for i in range(20):
            data = {'name': 'loc' + str(i),
                    'description': 'description' + str(i)}
            response = self.client.get('/regions/loc' + str(i) + '/')
            compare_data(self, response.data, data, ['name', 'description'])

    def test_delete_region_detail_permission_denied(self):
        """Ensure denied if not authenticated."""
        response = self.client.delete('/regions/loc1/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class Service_List_Tests(APITestCase):

    def test_post_services_list_fail_1(self):
        """Should return a 405 code even when logged in."""
        login_client(self.client)
        data = {'name': 'service1', 'description': 'this is a service',
                'rate': '0.5'}
        response = self.client.post('/regions/loc1/services/',
                                    data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_services_list_permission_denied(self):
        """Checks that post attempt is denied."""
        data = {'name': 'service1', 'description': 'this is a service',
                'rate': '0.5'}
        response = self.client.post('/regions/loc1/services/',
                                    data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_services_list(self):
        """Tests that all created services are listed."""
        login_client(self.client)
        rates = dict()
        services = []
        for i in range(10):
            data = {'name': 'serv' + str(i),
                    'pretty_name': 'Service ' + str(i),
                    'description': 'this is a service type'}
            services.append(data['name'])
            self.client.post('/service_types/', data, format='json')
            rates['serv' + str(i) + "_rate"] = i * 7
        data = {'name': 'loc1', 'description': 'this is a region'}
        data = dict(rates.items() + data.items())
        self.client.post('/regions/', data, format='json')

        service_list = []
        for service in self.client.get('/regions/loc1/services/').data:
            service_list.append(service['service_type'])

        for service in services:
            self.assertTrue(service_list.__contains__(service))


class Service_Detail_Tests(APITestCase):

    def test_put_service_detail_fail_1(self):
        """Checks that you are unable to put even if logged in."""
        login_client(self.client)
        data = {'name': 'service2', 'description': 'this is the same service',
                'region': 'loc1'}
        response = self.client.put('/regions/loc1/services/service1/',
                                   data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_service_detail_fail(self):
        """Checks that you are unable to patch even if logged in."""
        login_client(self.client)
        data = {'name': 'service2', 'description': 'this is the same service',
                'region': 'loc1'}
        response = self.client.patch('/regions/loc1/services/service1/',
                                     data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_service_detail(self):
        """Checks that all added services can be gotten."""
        login_client(self.client)
        rates = dict()
        services = []
        for i in range(10):
            data = {'name': 'serv' + str(i),
                    'pretty_name': 'Service ' + str(i),
                    'description': 'this is a service type'}
            services.append(data['name'])
            self.client.post('/service_types/', data, format='json')
            rates['serv' + str(i) + "_rate"] = i * 7
        data = {'name': 'loc1', 'description': 'this is a region'}
        data = dict(rates.items() + data.items())
        self.client.post('/regions/', data, format='json')

        for i in range(10):
            response = self.client.get('/regions/loc1/services/serv' +
                                       str(i) + '/')
            self.assertEqual(response.data['service_type'], services[i])

    def test_delete_service_detail_permission_denied(self):
        """Ensure permissions denied if not authenticated."""
        response = self.client.delete('/regions/loc1/services/service1/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class Rate_List_Tests(APITestCase):

    def test_post_rate_list_1(self):
        """Checks you are able to post new rates for a service,
           at the default date."""
        login_client(self.client)
        create_region_and_services(self, 'serv1', 'loc1', 5)
        data = {'rate': '17'}
        response = self.client.post('/regions/loc1/services/serv1/' +
                                    'rates/', data, format='json')
        self.assertEqual(response.data['rate'], '17')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_rate_list_2(self):
        """Checks that you can create a new rate at a given date."""
        login_client(self.client)
        create_region_and_services(self, 'serv1', 'loc1', 5)
        now = create_date()
        date = str(now.day) + '/' + str(now.month) + '/' + str(now.year)
        data = {'rate': '17', 'date': date}
        response = self.client.post('/regions/loc1/services/serv1/' +
                                    'rates/', data, format='json')
        self.assertEqual(response.data['rate'], '17')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_rate_list_permission_denied(self):
        """Ensure can't post if not authenticated."""
        now = create_date()
        date = str(now.day) + '/' + str(now.month) + '/' + str(now.year)
        data = {'rate': '17', 'date': date}
        response = self.client.post('/regions/loc1/services/service1/' +
                                    'rates/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_rate_list(self):
        """"""
        login_client(self.client)
        create_region_and_services(self, 'serv1', 'loc1', 5)
        rates = [{'rate': '5.0'}]
        for i in range(20):
            data = {'rate': str(float(i / 10))}
            rates.append(data)
            response = self.client.post('/regions/loc1/services/serv1/' +
                                        'rates/', data, format='json')
        response = self.client.get('/regions/loc1/services/serv1/rates/')
        for i in range(21):
            self.assertEqual(str(response.data[i]['rate']), rates[i]['rate'])


class Rate_detail_Tests(APITestCase):

    def test_get_current(self):
        """Checks that you are able to get the current rate for a service."""
        login_client(self.client)
        create_region_and_services(self, 'serv1', 'loc1', 0.7)
        response = self.client.get('/regions/loc1/services/serv1/' +
                                   'rates/current/')
        self.assertEqual(response.data['rate'], 0.7)

    def test_get_future(self):
        """Checks that you are able to get the next rate for a service."""
        login_client(self.client)
        create_region_and_services(self, 'serv1', 'loc1', 0.7)
        response = self.client.get('/regions/loc1/services/serv1/' +
                                   'rates/future/')
        # no 'future' rate, should have returned current (0.7):
        self.assertEqual(response.data['rate'], 0.7)
        now = create_date(days=5)
        date = str(now.day) + '/' + str(now.month) + '/' + str(now.year)
        data = {'rate': '17', 'date': date}
        self.client.post('/regions/loc1/services/serv1/' +
                         'rates/', data, format='json')
        response = self.client.get('/regions/loc1/services/serv1/' +
                                   'rates/future/')
        self.assertEqual(response.data['rate'], 17)
