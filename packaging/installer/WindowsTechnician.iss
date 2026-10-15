#define AppName "Windows Technician"
#define AppVersion "1.0.0"
#define AppPublisher "Windows Technician"
#define AppId "{C91E6F4A-82D3-4C51-A7B8-5E2F94D061AC}"

[Setup]
AppId={{C91E6F4A-82D3-4C51-A7B8-5E2F94D061AC}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Windows Technician
DefaultGroupName=Windows Technician
DisableProgramGroupPage=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
OutputDir=..\..\artifacts\v1.0.0\installer
OutputBaseFilename=WindowsTechnician-Setup-1.0.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#AppName}
VersionInfoVersion=1.0.0.0
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "..\..\installer_staging\Windows Technician\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Windows Technician"; Filename: "{app}\WindowsTechnician.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\Windows Technician"; Filename: "{app}\WindowsTechnician.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\WindowsTechnician.exe"; Description: "Launch Windows Technician"; Flags: postinstall nowait skipifsilent

[Code]
function VersionPart(const Version: String; Index: Integer): Integer;
var
  Remaining, Part: String;
  P, I: Integer;
begin
  Remaining := Version;
  Result := 0;

  for I := 0 to Index - 1 do
  begin
    P := Pos('.', Remaining);
    if P = 0 then
    begin
      Exit;
    end;
    Delete(Remaining, 1, P);
  end;

  P := Pos('.', Remaining);
  if P > 0 then
    Part := Copy(Remaining, 1, P - 1)
  else
    Part := Remaining;

  Result := StrToIntDef(Part, 0);
end;
function CompareVersions(const LeftVersion, RightVersion: String): Integer;
var
  I, L, R: Integer;
begin
  Result := 0;
  for I := 0 to 3 do
  begin
    L := VersionPart(LeftVersion, I);
    R := VersionPart(RightVersion, I);
    if L < R then
    begin
      Result := -1;
      Exit;
    end;
    if L > R then
    begin
      Result := 1;
      Exit;
    end;
  end;
end;

function InitializeSetup(): Boolean;
var
  PreviousVersion: String;
  UninstallKey: String;
begin
  Result := True;
  UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppId}_is1';

  if RegQueryStringValue(HKLM64, UninstallKey, 'DisplayVersion', PreviousVersion) then
  begin
    if CompareVersions(PreviousVersion, '{#AppVersion}') > 0 then
    begin
      MsgBox(
        'A newer version (' + PreviousVersion + ') is already installed.' +
        Chr(13) + Chr(10) + 'This installer will not downgrade Windows Technician.',
        mbError, MB_OK);
      Result := False;
    end;
  end;
end;
