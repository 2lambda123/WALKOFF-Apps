from unittest import TestCase
from apps.HelloWorld import main


class TestMain(TestCase):
    def setUp(self):
        self.app = main.Main()

    def test_hello_world(self):
        message = self.app.helloWorld()
        self.assertDictEqual(message, {"message": "HELLO WORLD"})

    def test_repeat_to_me(self):
        args = {'call': (lambda: 'test_message')}
        self.assertEqual(self.app.repeatBackToMe(args), 'REPEATING: {0}'.format('test_message'))

    def test_plus_one(self):
        args = {'number': (lambda: '4')}
        self.assertEqual(self.app.returnPlusOne(args), '5')
        with self.assertRaises(ValueError):
            self.app.returnPlusOne({'number': (lambda: 'aa')})

    def test_shutdown(self):
        self.assertIsNone(self.app.shutdown())

