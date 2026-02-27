; ClipStream Installer Script for Inno Setup
; This creates a professional Windows installer (.exe)
;
; Prerequisites:
; 1. Download Inno Setup from: https://jrsoftware.org/isdl.php
; 2. Compile this script with Inno Setup Compiler
;
; Output: A Setup.exe installer that users can run

#define AppName "ClipStream"
#define AppVersion "1.0.0"
#define AppPublisher "ClipStream"
#define AppExeName "ClipStream.bat"
#define AppPublisherURL "https://github.com/yourusername/clipstream"
#define AppSupportURL "https://github.com/yourusername/clipstream/issues"

[Setup]
; Installer configuration
AppId={{A1B2C3D4-E5F6-4A5B-8C7D-1E2F3A4B5C6D}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppPublisherURL}
AppSupportURL={#AppSupportURL}
AppUpdatesURL={#AppPublisherURL}
DefaultDirName={autopf}\ClipStream
DefaultGroupName=ClipStream
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=ClipStream-Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; Requires Windows 10 or later
MinVersion=10.0
; Show a license file (optional)
; LicenseFile=LICENSE.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Languages\English.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
Name: "quicklaunchicon"; Description: "Create a &quick launch icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Application files to be installed
Source: "app.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "utils.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "clipper.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "launcher.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
; Note: Add README and any other files you want to include

; Launcher batch file
Source: "ClipStream.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Program menu shortcut
Name: "{group}\ClipStream"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\app_icon.ico"
Name: "{group}\Uninstall ClipStream"; Filename: "{uninstallexe}"

; Desktop shortcut (if selected)
Name: "{autodesktop}\ClipStream"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon; IconFilename: "{app}\app_icon.ico"

; Quick launch shortcut (if selected)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\ClipStream"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Run]
; Run the app after installation (optional - user can choose)
Filename: "{app}\{#AppExeName}"; Description: "Launch ClipStream"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Delete temp folder on uninstall
Type: filesandordirs; Name: "{app}\temp"

[Code]
// Check if Python is installed
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  PythonInstalled: Boolean;
begin
  // Check if Python is in PATH
  PythonInstalled := False;

  // Try to find Python by checking the registry
  if RegQueryStringValue(HKLM, 'SOFTWARE\Python\PythonCore\', '', '') or
     RegQueryStringValue(HKCU, 'SOFTWARE\Python\PythonCore\', '', '') then
    PythonInstalled := True
  else
  begin
    // Try running python --version
    if ShellExec('', 'python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
      PythonInstalled := (ResultCode = 0);
  end;

  if not PythonInstalled then
  begin
    if MsgBox('ClipStream requires Python 3.9 or later to be installed.' + #13#10 +
              'Python was not found on your system.' + #13#10 + #13#10 +
              'Click Yes to download Python from python.org' + #13#10 +
              'Click No to exit the installer.',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Open Python download page
      ShellExec('open', 'https://www.python.org/downloads/', '', '', SW_SHOWNORMAL, ewNoWait, ResultCode);
    end;
    Result := False;
    Exit;
  end;

  Result := True;
end;

// Install dependencies after files are copied
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Show a progress message
    WizardForm.StatusLabel.Caption := 'Installing Python dependencies...';
    WizardForm.ProgressGauge.Style := pbstMarquee;
    WizardForm.ProgressGauge.Animate := True;
    WizardForm.Refresh;

    // Install pip requirements
    if ShellExec('', 'pip', 'install -q -r "' + ExpandConstant('{app}\requirements.txt') + '"',
                 '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0) then
    begin
      // Success
    end
    else
    begin
      // Show warning but don't fail
      MsgBox('Warning: Some dependencies may not have installed correctly.' + #13#10 +
             'You can install them manually by running: pip install -r requirements.txt' + #13#10 +
             'in the installation folder: ' + ExpandConstant('{app}'),
             mbInformation, MB_OK);
    end;
  end;
end;
