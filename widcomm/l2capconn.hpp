#pragma once

class WCL2CapConn : public CL2CapConn {
    public:
        enum {
            DATA_RECEIVED,
            INCOMING_CONNECTION,
            REMOTE_DISCONNECTED,
            CONNECTED
        };

        WCL2CapConn (PyObject *pyobj);
        virtual ~WCL2CapConn ();

        int AcceptClient ();

        inline unsigned short GetSockPort () { return sockport; }

    private:
        CL2CapIf rfcommif;
        void OnIncomingConnection ();
        void OnConnectPendingReceived ();
        void OnConnected ();
        void OnDataReceived (void *p_data, UINT16 len);
        void OnCongestionStatus (BOOL is_congested);
        void OnRemoteDisconnected (UINT16 reason);
        
        PyObject * pyobj;
        SOCKET threadfd;
        SOCKET serverfd;
        unsigned short sockport;
};
