import serial
import time


def readline(port):
    """
    重写readline方法，首先用in_waiting方法获取IO buffer中是否有值：
    如果有值，读取直到\n；
    如果有值，超过1S，直接返回；
    如果没有值，返回 ''
    :param port: 已经打开的端口
    :return: buf:端口读取到的值；没有值返回 ''
    """
    buf = ''
    try:
        if port.in_waiting > 0:
            start_time = time.time()
            while True:
                buf += port.read(1).decode('utf-8', 'replace')
                if buf.endswith('\n'):
                    print(buf.encode('utf-8'))
                    break  # 如果以\n结尾，停止读取
                elif time.time() - start_time > 1:
                    print('异常 {}'.format(repr(buf)).encode('utf-8'))
                    break  # 如果时间>1S(超时异常情况)，停止读取
    except OSError as error:
        print('Fatal ERROR: {}'.format(error).encode('utf-8'))
    finally:
        return buf


class Connection:
    def __init__(self):
        self._state = None
        self.new_state(ClosedConnectionState)

    def new_state(self, new_state):
        self._state = new_state

    def read(self):
        return self._state.read(self)

    def write(self, data):
        return self._state.write(self, data)

    def open(self):
        return self._state.open(self)

    def close(self):
        return self._state.close(self)


class ConnectionState:
    @staticmethod
    def read(conn):
        raise NotImplementedError()

    @staticmethod
    def write(conn, data):
        raise NotImplementedError()

    @staticmethod
    def open(conn):
        raise NotImplementedError()

    @staticmethod
    def close(conn):
        raise NotImplementedError()


class ClosedConnectionState(ConnectionState):
    @staticmethod
    def read(conn):
        global at_port
        while True:
            time.sleep(0.001)
            try:
                try:
                    at_port = serial.Serial(at_port, baudrate='115200', timeout=0)
                except ValueError:
                    at_port.open()
                finally:
                    break
            except serial.serialutil.SerialException:
                continue
        conn.new_state(OpenConnectionState)
        readline(at_port)

    @staticmethod
    def write(conn, data):
        global at_port
        while True:
            time.sleep(0.001)
            try:
                try:
                    at_port = serial.Serial(at_port, baudrate='115200', timeout=0)
                except ValueError:
                    at_port.open()
                finally:
                    break
            except serial.serialutil.SerialException:
                continue
        conn.new_state(OpenConnectionState)
        print('{}\r\n'.format(data).encode('utf-8'))
        at_port.write('{}\r\n'.format(data).encode('utf-8'))

    @staticmethod
    def open(conn):
        conn.new_state(OpenConnectionState)
        global at_port
        at_port = serial.Serial(at_port, baudrate=115200, timeout=0)

    @staticmethod
    def close(conn):
        global at_port
        if isinstance(at_port, str):
            pass
        else:
            at_port.close()


class OpenConnectionState(ConnectionState):
    @staticmethod
    def read(conn):
        global at_port
        try:
            readline(at_port)
        except serial.serialutil.SerialException:
            conn.new_state(ClosedConnectionState)

    @staticmethod
    def write(conn, data):
        global at_port
        try:
            at_port.write('{}\r\n'.format(data).encode('utf-8'))
            print('{}\r\n'.format(data).encode('utf-8'))
        except serial.serialutil.SerialException:
            conn.new_state(ClosedConnectionState)

    @staticmethod
    def open(conn):
        pass

    @staticmethod
    def close(conn):
        conn.new_state(ClosedConnectionState)


if __name__ == '__main__':
    at_port = "COM11"
    c = Connection()
    c.write('AT')
    while True:
        c.read()
