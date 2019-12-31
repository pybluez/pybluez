#!/usr/bin/env python3
"""PyBluez example bluezchat.py

A simple graphical chat client to demonstrate the use of pybluez.

Opens a l2cap socket and listens on PSM 0x1001.

Provides the ability to scan for nearby bluetooth devices and establish chat
sessions with them.
"""

import gtk
import gobject
import gtk.glade

import bluetooth
import bluetooth._bluetooth as bluez

GLADEFILE = "bluezchat.glade"

# *****************

def alert(text, buttons=gtk.BUTTONS_NONE, type=gtk.MESSAGE_INFO):
    md = gtk.MessageDialog(buttons=buttons, type=type)
    md.label.set_text(text)
    md.run()
    md.destroy()


class BluezChatGui:
    def __init__(self):
        self.main_window_xml = gtk.glade.XML(GLADEFILE, "bluezchat_window")

        # connect our signal handlers
        dic = {"on_quit_button_clicked": self.quit_button_clicked,
               "on_send_button_clicked": self.send_button_clicked,
               "on_chat_button_clicked": self.chat_button_clicked,
               "on_scan_button_clicked": self.scan_button_clicked,
               "on_devices_tv_cursor_changed": self.devices_tv_cursor_changed}

        self.main_window_xml.signal_autoconnect(dic)

        # prepare the floor listbox
        self.devices_tv = self.main_window_xml.get_widget("devices_tv")
        self.discovered = gtk.ListStore(gobject.TYPE_STRING,
                                        gobject.TYPE_STRING)
        self.devices_tv.set_model(self.discovered)
        renderer = gtk.CellRendererText()
        column1 = gtk.TreeViewColumn("addr", renderer, text=0)
        column2 = gtk.TreeViewColumn("name", renderer, text=1)
        self.devices_tv.append_column(column1)
        self.devices_tv.append_column(column2)

        self.quit_button = self.main_window_xml.get_widget("quit_button")
        self.scan_button = self.main_window_xml.get_widget("scan_button")
        self.chat_button = self.main_window_xml.get_widget("chat_button")
        self.send_button = self.main_window_xml.get_widget("send_button")
        self.main_text = self.main_window_xml.get_widget("main_text")
        self.input_tb = self.main_window_xml.get_widget("input_tb")
        self.text_buffer = self.main_text.get_buffer()
        self.chat_button.set_sensitive(False)

        self.listed_devs = []
        self.peers = {}
        self.sources = {}
        self.addresses = {}

        # the listening sockets
        self.server_sock = None

    # --- gui signal handlers

    def quit_button_clicked(self, widget):
        gtk.main_quit()

    def scan_button_clicked(self, widget):
        self.quit_button.set_sensitive(False)
        self.scan_button.set_sensitive(False)
        # self.chat_button.set_sensitive(False)

        self.discovered.clear()
        for addr, name in bluetooth.discover_devices(lookup_names=True):
            self.discovered.append((addr, name))

        self.quit_button.set_sensitive(True)
        self.scan_button.set_sensitive(True)
        # self.chat_button.set_sensitive(True)

    def send_button_clicked(self, widget):
        text = self.input_tb.get_text()
        if not text:
            return

        for addr, sock in list(self.peers.items()):
            sock.send(text)

        self.input_tb.set_text("")
        self.add_text("\nme - " + text)

    def chat_button_clicked(self, widget):
        (model, iter) = self.devices_tv.get_selection().get_selected()
        if iter is not None:
            addr = model.get_value(iter, 0)
            if addr not in self.peers:
                self.add_text("\nconnecting to " + addr)
                self.connect(addr)
            else:
                self.add_text("\nAlready connected to " + addr)

    def devices_tv_cursor_changed(self, widget):
        (model, iter) = self.devices_tv.get_selection().get_selected()
        if iter is not None:
            self.chat_button.set_sensitive(True)
        else:
            self.chat_button.set_sensitive(False)

    # --- network events

    def incoming_connection(self, source, condition):
        sock, info = self.server_sock.accept()
        address, psm = info

        self.add_text("\naccepted connection from " + str(address))

        # add new connection to list of peers
        self.peers[address] = sock
        self.addresses[sock] = address

        source = gobject.io_add_watch(sock, gobject.IO_IN, self.data_ready)
        self.sources[address] = source
        return True

    def data_ready(self, sock, condition):
        address = self.addresses[sock]
        data = sock.recv(1024)

        if not data:
            self.add_text("\nlost connection with " + address)
            gobject.source_remove(self.sources[address])
            del self.sources[address]
            del self.peers[address]
            del self.addresses[sock]
            sock.close()
        else:
            self.add_text("\n{} - {}".format(address, str(data)))
        return True

    # --- other stuff

    def cleanup(self):
        self.hci_sock.close()

    def connect(self, addr):
        sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        try:
            sock.connect((addr, 0x1001))
        except bluez.error as e:
            self.add_text("\n" + str(e))
            sock.close()
            return

        self.peers[addr] = sock
        source = gobject.io_add_watch(sock, gobject.IO_IN, self.data_ready)
        self.sources[addr] = source
        self.addresses[sock] = addr

    def add_text(self, text):
        self.text_buffer.insert(self.text_buffer.get_end_iter(), text)

    def start_server(self):
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.server_sock.bind(("", 0x1001))
        self.server_sock.listen(1)

        gobject.io_add_watch(self.server_sock, gobject.IO_IN,
                             self.incoming_connection)

    def run(self):
        self.text_buffer.insert(self.text_buffer.get_end_iter(), "loading...")
        self.start_server()
        gtk.main()


if __name__ == "__main__":
    gui = BluezChatGui()
    gui.run()
