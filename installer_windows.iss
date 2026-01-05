; Inno Setup Script for JarvisMonitor
; Download Inno Setup from: https://jrsoftware.org/isinfo.php

[Setup]
AppName=JarvisMonitor
AppVersion=1.0
AppPublisher=JarvisMonitor
DefaultDirName={autopf}\JarvisMonitor
DefaultGroupName=JarvisMonitor
OutputDir=installer
OutputBaseFilename=JarvisMonitor_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Files]
; Include the entire dist\JarvisMonitor folder
Source: "dist\JarvisMonitor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
; Desktop shortcut
Name: "{autodesktop}\JarvisMonitor"; Filename: "{app}\JarvisMonitor.exe"
; Start menu shortcut
Name: "{group}\JarvisMonitor"; Filename: "{app}\JarvisMonitor.exe"
Name: "{group}\Uninstall JarvisMonitor"; Filename: "{uninstallexe}"

[Run]
; Option to run after install
Filename: "{app}\JarvisMonitor.exe"; Description: "Launch JarvisMonitor"; Flags: nowait postinstall skipifsilent
