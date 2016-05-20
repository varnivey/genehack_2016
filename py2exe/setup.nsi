;    This file is a part of DARFI project (dna Damage And Repair Foci Imager)
;    Copyright (C) 2014  Ivan V. Ozerov
;
;    This program is free software; you can redistribute it and/or modify
;    it under the terms of the GNU General Public License version 2 as·
;    published by the Free Software Foundation.
;
;    This program is distributed in the hope that it will be useful,
;    but WITHOUT ANY WARRANTY; without even the implied warranty of
;    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;    GNU General Public License v2 for more details.
;
;    You should have received a copy of the GNU General Public License along
;    with this program; if not, write to the Free Software Foundation, Inc.,
;    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

!define py2exeOutputDir 'dist'
!define exe             'darfi.exe'
!define icon            '..\misc\darfi.ico'
!define compressor      'lzma'  ;one of 'zlib', 'bzip2', 'lzma'
!define onlyOneInstance

; - - - - do not edit below this line, normaly - - - -
!ifdef compressor
    SetCompressor ${compressor}
!else
    SetCompress Off
!endif
Name ${exe}
OutFile ${exe}
SilentInstall silent
!ifdef icon
    Icon ${icon}
!endif

; - - - - Allow only one installer instance - - - - 
!ifdef onlyOneInstance
Function .onInit
 System::Call "kernel32::CreateMutexA(i 0, i 0, t '$(^Name)') i .r0 ?e"
 Pop $0
 StrCmp $0 0 launch
  Abort
 launch:
FunctionEnd
!endif
; - - - - Allow only one installer instance - - - - 

Section
    
    ; Get directory from which the exe was called
    System::Call "kernel32::GetCurrentDirectory(i ${NSIS_MAX_STRLEN}, t .r0)"
    
    ; Unzip into pluginsdir
    InitPluginsDir
    SetOutPath '$PLUGINSDIR'
    File /r '${py2exeOutputDir}\*.*'
    
    ; Set working dir and execute, passing through commandline params
    SetOutPath '$0'
;    ${GetParameters} $R0
    ExecWait '"$PLUGINSDIR\simple_gui.exe" $R0' $R2
    SetErrorLevel $R2
 
SectionEnd
