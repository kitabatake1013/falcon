#define UNICODE
#include <windows.h>
#include <string.h>
#include <iostream>
#include <vector>
#include <string>
using namespace std;

vector<string> wnds;

BOOL CALLBACK EnumChildProc(HWND hwnd, LPARAM lParam){
TCHAR className[512]={0};
GetClassName(hwnd,className,512);
if(lstrcmp(className,L"Button")!=0){
return 1;
}
LONG l=GetWindowLong(hwnd,-16);
//TCHAR windowText[512]={0};
//GetWindowText(hwnd,windowText,512);
//char c_out[512]={0};
//char t_out[512]={0};
//WideCharToMultiByte(CP_ACP, 0, className, -1, c_out, sizeof(c_out)-1, NULL, NULL);
//WideCharToMultiByte(CP_ACP, 0, windowText, -1, t_out, sizeof(t_out)-1, NULL, NULL);
//printf("index %d className %s style 0x%x text %s\n",count,c_out,l,t_out);
if(l%16==9){
wnds.push_back(to_string(reinterpret_cast<int>(hwnd)));
}
return 1;
}

int main(){
HWND WND=(HWND)3476208;
HWND parent=WND;
EnumChildWindows(parent,EnumChildProc,0);
string s;
for(int i=0;i<wnds.size();++i){
s+=wnds[i];
if(i!=wnds.size()-1){
s+=",";
}
}
cout << s << endl;
return 0;
}
