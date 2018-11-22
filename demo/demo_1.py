#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys, os, time, atexit
from signal import SIGTERM
import logging
import ConfigParser
from apscheduler.schedulers.background import BlockingScheduler
from python_test import PrintText

logger = logging.getLogger('mylogger')

config = ConfigParser.ConfigParser()
config.read('demo.conf')
WORKER_PATH = config.get('db_config', 'WORKER_PATH')
start_hour = config.get('server_start', 'start_hour')
start_minute = config.get('server_start', 'start_minute')

def log_text():
    # 创建一个logger
    log_path = WORKER_PATH
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG)
    # 创建一个handler，用于写入日志文件
    fh = logging.FileHandler(log_path+"/log_test.log")
    fh.setLevel(logging.DEBUG)
    # 定义handler的输出格式
    formatter = logging.Formatter(
        '[%(asctime)s][%(thread)d][%(filename)s][line: %(lineno)d][%(levelname)s] ## %(message)s')
    fh.setFormatter(formatter)
    # 给logger添加handler
    logger.addHandler(fh)

class Daemon:
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        # 需要获取调试信息，改为stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr'，以root身份运行。
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.logger = log_text()


    def _daemonize(self):
        try:
            pid = os.fork()  # 第一次fork，生成子进程，脱离父进程
            if pid > 0:
                sys.exit(0)  # 退出主进程
        except OSError, e:
            sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")  # 修改工作目录
        os.setsid()  # 设置新的会话连接
        os.umask(0)  # 重新设置文件创建权限

        try:
            pid = os.fork()  # 第二次fork，禁止进程打开终端
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        # 重定向文件描述符
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # 注册退出函数，根据文件pid判断是否存在进程
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write('%s\n' % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        logger.info('start....')
        # 检查pid文件是否存在以探测是否存在进程
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = 'pidfile %s already exist. Daemon already running!\n'
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # 启动监控
        self._daemonize()
        self._run()

    def stop(self):
        # 从pid文件中获取pid
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:  # 重启不报错
            message = 'pidfile %s does not exist. Daemon not running!\n'
            sys.stderr.write(message % self.pidfile)
            return

        # 杀进程
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
                # os.system('hadoop-daemon.sh stop datanode')
                # os.system('hadoop-daemon.sh stop tasktracker')
                # os.remove(self.pidfile)
        except OSError, err:
            err = str(err)
            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()

    def _run(self):
        """ run your fun"""
        scheduler = BlockingScheduler()
        scheduler.add_job(PrintText().start, 'interval', seconds=3)
        # scheduler.add_job(PrintText().start, 'cron',  hour=start_hour, minute=start_minute,second='0')
        try:
            scheduler.start()
        except KeyboardInterrupt, SystemExit:
            scheduler.shutdown()
            logger.error('Exit The Job!')


if __name__ == '__main__':
    # test = Daemon('/s')
    # test._run()
    daemon = Daemon('/tmp/watch_process.pid', stdout='/tmp/watch_stdout.log')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print 'unknown command'
            sys.exit(2)
        sys.exit(0)
    else:
        print 'usage: %s start|stop|restart' % sys.argv[0]
        sys.exit(2)
