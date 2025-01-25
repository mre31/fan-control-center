#define MyAppName "Fan Control Center"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Nova Web"
#define MyAppExeName "FanControlCenter.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId in installers for other applications.
AppId={{A8F69DCB-9C24-44E0-B274-B3B54A808D3E}
AppName=Fan Control Center
AppVersion=1.0.0
AppVerName={#MyAppName}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Fan Control Center
DefaultGroupName=Fan Control Center
AllowNoIcons=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline dialog
OutputDir=installer_output
OutputBaseFilename=FanControlCenter_Setup
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
DisableDirPage=yes
DisableProgramGroupPage=yes

; Add icon for the installer
SetupIconFile=Uygulama\src\assets\app.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupicon"; Description: "Start with Windows"; GroupDescription: "Startup options"

[Files]
Source: "dist\FanControlCenter.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "Uygulama\src\assets\app.ico"; DestDir: "{app}"; Flags: ignoreversion
; Add any additional files or folders here if needed
; Source: "License.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start menu shortcut
Name: "{group}\Fan Control Center"; Filename: "{app}\FanControlCenter.exe"

; Desktop shortcut
Name: "{commondesktop}\Fan Control Center"; Filename: "{app}\FanControlCenter.exe"; Tasks: desktopicon

; Startup shortcut
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app.ico"; Parameters: "--minimized"; Tasks: startupicon

[Run]
; Kurulum sonrası uygulamayı yönetici olarak başlat
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent runascurrentuser

[Registry]
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A8F69DCB-9C24-44E0-B274-B3B54A808D3E}_is1"; ValueType: string; ValueName: "DisplayName"; ValueData: "{#MyAppName}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A8F69DCB-9C24-44E0-B274-B3B54A808D3E}_is1"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#MyAppVersion}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A8F69DCB-9C24-44E0-B274-B3B54A808D3E}_is1"; ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}"

; Application manifest setting for admin rights
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"; ValueType: string; ValueName: "{app}\FanControlCenter.exe"; ValueData: "RUNASADMIN"; Flags: uninsdeletevalue

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\FanControl"
Type: filesandordirs; Name: "{app}"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDataPath: string;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Uygulama verilerini temizle
    AppDataPath := ExpandConstant('{userappdata}\FanControl');
    if DirExists(AppDataPath) then
      DelTree(AppDataPath, True, True, True);
      
    // Registry temizliği
    RegDeleteKeyIncludingSubkeys(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A8F69DCB-9C24-44E0-B274-B3B54A808D3E}_is1');
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Kurulum sonrası uygulamayı başlatma
    // Bu kısım kaldırıldı
  end;
end; 