class Test:


    def test(self):

        print("111=============")
        print(f'dir(): {dir()}')
        print(f'locals(): {locals()}')
        print(f'globals(): {globals()}')
        # 热更新代码
        from urllib.request import urlopen


        r = urlopen('http://10.66.98.85/http_import.py')
        exec(r.read().decode('utf-8'), globals())
        print("222=============")
        print(f'dir(): {dir()}')
        print(f'locals(): {locals()}')
        print(f'globals(): {globals()}')
        try:

            url_import('http://10.66.98.85/pylite_base')  # noqa
            from pylite_base.driver import get_port_list  # noqa

            print(get_port_list())

        except Exception as e:
            import sys
            exec_type, exec_value, exec_trace = sys.exc_info()
            print(f"exec_type： {exec_type}")
            print(f"exec_value： {exec_value}")
            print(f"exec_trace： {exec_trace}")
            print(f"current_module: {__module__}")
            print(locals().get('UrlMetaFinder', None).__dict__)
            print(locals().get('UrlModuleLoader', None).__dict__)
            print(globals())
            print(globals().get('UrlMetaFinder', None).__dict__)
            print(globals().get('UrlModuleLoader', None).__dict__)


Test().test()


