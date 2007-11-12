#pragma once

class WCRfCommPort : public CRfCommPort {
    public:
        enum {
            DATA_RECEIVED,
            EVENT_RECEIVED
        };

        WCRfCommPort (PyObject *pyobj);
        virtual ~WCRfCommPort ();

        int AcceptClient ();

        inline unsigned short GetSockPort () { return sockport; }

    private:
        CRfCommIf rfcommif;
        void OnDataReceived (void *p_data, UINT16 len);
        void OnEventReceived (UINT32 event_code);
        
        PyObject * pyobj;
        SOCKET threadfd;
        SOCKET serverfd;
        unsigned short sockport;
};
