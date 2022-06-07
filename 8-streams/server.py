import socket
import sys
from sys import argv, exit
import json
import logging
import select
import argparse
import time
from collections import deque

from common.utils import Utils
from common.variables import *
import log.server_log_config
from log.decorators import log, Log

SERVER_LOGGER = logging.getLogger('server_logger')


class Server(Utils):
    def __init__(self):
        self.listen_address: str = DEFAULT_LISTEN_ADDRESS
        self.listen_port: int = DEFAULT_PORT

        self.messages = deque()
        self.clients_socks = []
        self.client_message: dict = {}
        self.messages_list: list = []
        self.client_sock: socket = socket
        self.names_client_socks: dict = {}

        self.message_for_send: dict = {}

    @log
    def process_client_message(self) -> None:
        # SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')
        if (ACTION in self.client_message and
                self.client_message[ACTION] == PRESENCE and
                TIME in self.client_message and
                USER in self.client_message):
            if self.client_message[USER][ACCOUNT_NAME] not in self.names_client_socks.keys():
                self.names_client_socks[self.client_message[USER][ACCOUNT_NAME]] = self.client_sock
                self.send_message(self.client_sock, {RESPONSE: 200})
            else:
                response = RESPONSE_400
                response[ERROR] = NAME_IS_OCCUPIED
                self.send_message(self.client_sock, response)
                self.clients_socks.remove(self.client_sock)
            return
        elif (ACTION in self.client_message and self.client_message[ACTION] == MESSAGE and
              DESTINATION in self.client_message and SENDER in self.client_message and
              TIME in self.client_message and MESSAGE_TEXT in self.client_message):
            self.messages_list.append(self.client_message)
            return
        elif (ACTION in self.client_message and self.client_message[ACTION] == EXIT and
              ACCOUNT_NAME in self.client_message):
            self.clients_socks.remove(self.names_client_socks[self.client_message[ACCOUNT_NAME]])
            self.names_client_socks[self.client_message[ACCOUNT_NAME]].close()
            del self.names_client_socks[self.client_message[ACCOUNT_NAME]]
            return
        else:
            response = response = RESPONSE_400
            response[ERROR] = REQUEST_IS_INCORRECT
            self.send_message(self.client_sock, response)
        return

    @log
    def process_message(self, message, listen_socks: list) -> None:
        if message[DESTINATION] in self.names_client_socks and self.names_client_socks[
            message[DESTINATION]] in listen_socks:
            SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                               f'от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names_client_socks and self.names_client_socks[
            message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            SERVER_LOGGER.error(f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                                f'отправка сообщения невозможна.')

    @log
    def check_port(self) -> None:
        if self.listen_port < MIN_PORT_NUMBER or self.listen_port > MAX_PORT_NUMBER:
            SERVER_LOGGER.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {self.listen_port}. Допустимы адреса с {MIN_PORT_NUMBER} до {MAX_PORT_NUMBER}.')
            exit(1)

    @log
    def arguments_parser(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-a', default='', nargs='?')
        name_space = parser.parse_args(sys.argv[1:])
        self.listen_address = name_space.a
        self.listen_port = name_space.p
        self.check_port()

    @Log()
    def main(self):
        self.arguments_parser()

        # SERVER_LOGGER.info(
        #     f'Запущен сервер, порт для подключений: {self.listen_port}, адрес с которого принимаются подключения: '
        #     f'{self.listen_address or "любой"}. Если адрес не указан, принимаются соединения с любых адресов.')

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.listen_address, self.listen_port))
        transport.settimeout(0.5)
        transport.listen(MAX_CONNECTIONS)

        while True:
            try:
                client, client_address = transport.accept()
                self.client_sock = client
                # SERVER_LOGGER.info('сервер ожидает запроса')
            except OSError:
                pass
            else:
                SERVER_LOGGER.info(f'Установлено соединение с {client_address}')
                self.clients_socks.append(self.client_sock)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            try:
                if self.clients_socks:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients_socks, self.clients_socks, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.client_message = self.get_message(client_with_message)
                        self.process_client_message()
                    except Exception:
                        SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients_socks.remove(client_with_message)

            for item in self.messages:
                try:
                    self.process_message(message=item, listen_socks=send_data_lst)
                except Exception:
                    SERVER_LOGGER.info(f'Связь с клиентом с именем {item[DESTINATION]} была потеряна')
                    self.clients_socks.remove(self.names_client_socks[item[DESTINATION]])
                    del self.names_client_socks[item[DESTINATION]]
            self.messages.clear()


if __name__ == '__main__':
    server = Server()
    server.main()
