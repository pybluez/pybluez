#pragma once

class WCInquirer : public CBtIf {
    public:
        enum {
            DEVICE_RESPONDED,
            INQUIRY_COMPLETE,
            DISCOVERY_COMPLETE,
            STACK_STATUS_CHAGE
        };
        
        WCInquirer::WCInquirer (PyObject *wcinq);

        virtual ~WCInquirer ();

        int AcceptClient ();

        inline unsigned short GetSockPort () { return sockport; }
        
    private:
        void OnDeviceResponded (BD_ADDR bda, DEV_CLASS devClass, 
                BD_NAME bdName, BOOL bConnected);
        void OnInquiryComplete (BOOL success, short num_responses);
        void OnDiscoveryComplete ();
        void OnStackStatusChange (STACK_STATUS new_status);

        PyObject * wcinq;
        SOCKET threadfd;
        SOCKET serverfd;
        unsigned short sockport;
};


