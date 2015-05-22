#include <windows.h>

#include "util.h"

namespace PyWidcomm {

int 
str2uuid( const char *uuid_str, GUID *uuid) 
{
    // Parse uuid128 standard format: 12345678-9012-3456-7890-123456789012
    int i;
    char buf[20] = { 0 };

    strncpy_s(buf, sizeof(buf), uuid_str, 8);
    uuid->Data1 = strtoul( buf, NULL, 16 );
    memset(buf, 0, sizeof(buf));

    strncpy_s(buf, sizeof(buf), uuid_str+9, 4);
    uuid->Data2 = (unsigned short) strtoul( buf, NULL, 16 );
    memset(buf, 0, sizeof(buf));
    
    strncpy_s(buf, sizeof(buf), uuid_str+14, 4);
    uuid->Data3 = (unsigned short) strtoul( buf, NULL, 16 );
    memset(buf, 0, sizeof(buf));

    strncpy_s(buf, sizeof(buf), uuid_str+19, 4);
    strncpy_s(buf+4, sizeof(buf)-4, uuid_str+24, 12);
    for( i=0; i<8; i++ ) {
        char buf2[3] = { buf[2*i], buf[2*i+1], 0 };
        uuid->Data4[i] = (unsigned char)strtoul( buf2, NULL, 16 );
    }

    return 0;
}

}
