using System;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Windows.Forms;
using System.Drawing;
using System.Runtime.InteropServices;
using Microsoft.Win32;
using System.Diagnostics;

namespace HavenInstaller
{
    public class InstallerForm : Form
    {
        private ProgressBar progressBar;
        private Label statusLabel;
        private Label titleLabel;
        private Label subTitleLabel;
        private TextBox pathBox;
        private Button installButton;
        private Button browseButton;
        private CheckBox chkPath;
        private CheckBox chkDesktop;
        private CheckBox chkStartMenu;
        private CheckBox chkFileAssoc;
        private CheckBox chkLaunchIde;

        [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
        private static extern IntPtr SendMessageTimeout(IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);

        private static readonly IntPtr HWND_BROADCAST = new IntPtr(0xffff);
        private const uint WM_SETTINGCHANGE = 0x001A;
        private const uint SMTO_ABORTIFHUNG = 0x0002;

        public InstallerForm()
        {
            this.Text = "Haven Programming Language v1.0.0 Setup";
            this.Size = new Size(580, 480);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.BackColor = Color.FromArgb(245, 247, 250);

            // Title Header Panel
            Panel headerPanel = new Panel();
            headerPanel.Size = new Size(580, 80);
            headerPanel.BackColor = Color.FromArgb(15, 23, 42); // Dark slate
            this.Controls.Add(headerPanel);

            titleLabel = new Label();
            titleLabel.Text = "Haven Programming Language 1.0.0";
            titleLabel.Font = new Font("Segoe UI", 14, FontStyle.Bold);
            titleLabel.ForeColor = Color.FromArgb(56, 189, 248); // Cyan
            titleLabel.Location = new Point(20, 15);
            titleLabel.AutoSize = true;
            headerPanel.Controls.Add(titleLabel);

            subTitleLabel = new Label();
            subTitleLabel.Text = "ODCS Native Production Release • Created by Anirudha Puthraya";
            subTitleLabel.Font = new Font("Segoe UI", 9, FontStyle.Regular);
            subTitleLabel.ForeColor = Color.FromArgb(203, 213, 225);
            subTitleLabel.Location = new Point(22, 45);
            subTitleLabel.AutoSize = true;
            headerPanel.Controls.Add(subTitleLabel);

            // Installation Path selection
            Label lblPath = new Label();
            lblPath.Text = "Install Location:";
            lblPath.Font = new Font("Segoe UI", 9, FontStyle.Bold);
            lblPath.Location = new Point(25, 100);
            lblPath.AutoSize = true;
            this.Controls.Add(lblPath);

            string defaultPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Programs", "Haven");
            pathBox = new TextBox();
            pathBox.Text = defaultPath;
            pathBox.Font = new Font("Segoe UI", 9);
            pathBox.Location = new Point(25, 125);
            pathBox.Size = new Size(420, 25);
            this.Controls.Add(pathBox);

            browseButton = new Button();
            browseButton.Text = "Browse...";
            browseButton.Location = new Point(455, 123);
            browseButton.Size = new Size(90, 28);
            browseButton.Click += (s, e) => {
                using (FolderBrowserDialog fbd = new FolderBrowserDialog())
                {
                    fbd.SelectedPath = pathBox.Text;
                    if (fbd.ShowDialog() == DialogResult.OK)
                    {
                        pathBox.Text = fbd.SelectedPath;
                    }
                }
            };
            this.Controls.Add(browseButton);

            // Options checkboxes
            chkPath = new CheckBox();
            chkPath.Text = "Add Haven to system environment PATH (Recommended)";
            chkPath.Checked = true;
            chkPath.Font = new Font("Segoe UI", 9);
            chkPath.Location = new Point(25, 165);
            chkPath.AutoSize = true;
            this.Controls.Add(chkPath);

            chkDesktop = new CheckBox();
            chkDesktop.Text = "Create Desktop shortcut for Haven IDE (ODCS Edition)";
            chkDesktop.Checked = true;
            chkDesktop.Font = new Font("Segoe UI", 9);
            chkDesktop.Location = new Point(25, 195);
            chkDesktop.AutoSize = true;
            this.Controls.Add(chkDesktop);

            chkStartMenu = new CheckBox();
            chkStartMenu.Text = "Create Start Menu shortcuts for Haven 1.0.0 & IDLE";
            chkStartMenu.Checked = true;
            chkStartMenu.Font = new Font("Segoe UI", 9);
            chkStartMenu.Location = new Point(25, 225);
            chkStartMenu.AutoSize = true;
            this.Controls.Add(chkStartMenu);

            chkFileAssoc = new CheckBox();
            chkFileAssoc.Text = "Associate .hvn and .haven source files with Haven & Haven IDE";
            chkFileAssoc.Checked = true;
            chkFileAssoc.Font = new Font("Segoe UI", 9);
            chkFileAssoc.Location = new Point(25, 255);
            chkFileAssoc.AutoSize = true;
            this.Controls.Add(chkFileAssoc);

            chkLaunchIde = new CheckBox();
            chkLaunchIde.Text = "Launch Haven IDE after installation completes";
            chkLaunchIde.Checked = true;
            chkLaunchIde.Font = new Font("Segoe UI", 9, FontStyle.Bold);
            chkLaunchIde.ForeColor = Color.FromArgb(14, 116, 144);
            chkLaunchIde.Location = new Point(25, 290);
            chkLaunchIde.AutoSize = true;
            this.Controls.Add(chkLaunchIde);

            // Status label & progress bar
            statusLabel = new Label();
            statusLabel.Text = "Ready to install.";
            statusLabel.Font = new Font("Segoe UI", 8.5f, FontStyle.Italic);
            statusLabel.Location = new Point(25, 330);
            statusLabel.Size = new Size(520, 20);
            this.Controls.Add(statusLabel);

            progressBar = new ProgressBar();
            progressBar.Location = new Point(25, 355);
            progressBar.Size = new Size(520, 22);
            progressBar.Style = ProgressBarStyle.Continuous;
            this.Controls.Add(progressBar);

            // Install Button
            installButton = new Button();
            installButton.Text = "Install Haven Now";
            installButton.Font = new Font("Segoe UI", 10, FontStyle.Bold);
            installButton.BackColor = Color.FromArgb(2, 132, 199);
            installButton.ForeColor = Color.White;
            installButton.FlatStyle = FlatStyle.Flat;
            installButton.FlatAppearance.BorderSize = 0;
            installButton.Location = new Point(365, 395);
            installButton.Size = new Size(180, 36);
            installButton.Click += (s, e) => PerformInstall();
            this.Controls.Add(installButton);
        }

        private void PerformInstall()
        {
            installButton.Enabled = false;
            browseButton.Enabled = false;
            pathBox.Enabled = false;

            string targetDir = pathBox.Text.Trim();

            try
            {
                UpdateStatus("Extracting Haven v1.0.0 runtime and modules...", 20);
                Directory.CreateDirectory(targetDir);

                // Extract embedded ZIP resource
                Assembly asm = Assembly.GetExecutingAssembly();
                string resourceName = null;
                foreach (string name in asm.GetManifestResourceNames())
                {
                    if (name.EndsWith(".zip", StringComparison.OrdinalIgnoreCase))
                    {
                        resourceName = name;
                        break;
                    }
                }

                if (resourceName != null)
                {
                    using (Stream s = asm.GetManifestResourceStream(resourceName))
                    using (ZipArchive archive = new ZipArchive(s))
                    {
                        int count = archive.Entries.Count;
                        int idx = 0;
                        foreach (ZipArchiveEntry entry in archive.Entries)
                        {
                            string destPath = Path.Combine(targetDir, entry.FullName);
                            if (string.IsNullOrEmpty(entry.Name))
                            {
                                Directory.CreateDirectory(destPath);
                            }
                            else
                            {
                                Directory.CreateDirectory(Path.GetDirectoryName(destPath));
                                entry.ExtractToFile(destPath, true);
                            }
                            idx++;
                            if (idx % 50 == 0)
                            {
                                UpdateStatus(string.Format("Extracting: {0}", entry.Name), 20 + (int)(idx * 50.0 / count));
                            }
                        }
                    }
                }
                else
                {
                    // Fallback if running directly alongside distribution
                    string localZip = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Haven-1.0.0-win64.zip");
                    if (File.Exists(localZip))
                    {
                        ZipFile.ExtractToDirectory(localZip, targetDir);
                    }
                }

                // 2. PATH Registration
                if (chkPath.Checked)
                {
                    UpdateStatus("Registering Haven in User environment PATH...", 75);
                    AddToPath(targetDir);
                }

                // 3. Desktop Shortcut
                if (chkDesktop.Checked)
                {
                    UpdateStatus("Creating Haven IDE Desktop shortcut...", 85);
                    string desktop = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
                    string havenw = Path.Combine(targetDir, "havenw.exe");
                    string icon = Path.Combine(targetDir, "haven.ico");
                    CreateShortcut(Path.Combine(desktop, "Haven IDE.lnk"), havenw, "-m idlelib", icon, "Haven IDE (ODCS Edition)");
                }

                // 4. Start Menu Shortcuts
                if (chkStartMenu.Checked)
                {
                    UpdateStatus("Creating Start Menu shortcuts...", 90);
                    string startMenu = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Programs), "Haven 1.0.0");
                    Directory.CreateDirectory(startMenu);
                    string havenExe = Path.Combine(targetDir, "haven.exe");
                    string havenw = Path.Combine(targetDir, "havenw.exe");
                    string icon = Path.Combine(targetDir, "haven.ico");
                    string uninstBat = Path.Combine(targetDir, "uninstall.bat");

                    CreateShortcut(Path.Combine(startMenu, "Haven 1.0.0 (Command Line).lnk"), havenExe, "", icon, "Haven 1.0.0 Command Line");
                    CreateShortcut(Path.Combine(startMenu, "Haven IDE (IDLE).lnk"), havenw, "-m idlelib", icon, "Haven IDE (ODCS Edition)");
                    CreateShortcut(Path.Combine(startMenu, "Uninstall Haven.lnk"), uninstBat, "", "", "Uninstall Haven");
                }

                // 5. File Associations
                if (chkFileAssoc.Checked)
                {
                    UpdateStatus("Registering .hvn and .haven file associations...", 95);
                    RegisterFileAssociations(targetDir);
                }

                // 6. Write Uninstaller
                WriteUninstaller(targetDir);

                UpdateStatus("Installation completed successfully!", 100);
                progressBar.Value = 100;
                installButton.Text = "Finished";
                installButton.BackColor = Color.FromArgb(16, 185, 129); // Green
                installButton.Enabled = true;
                installButton.Click += (s, e) => {
                    if (chkLaunchIde.Checked)
                    {
                        string havenw = Path.Combine(targetDir, "havenw.exe");
                        Process.Start(new ProcessStartInfo(havenw, "-m idlelib") { WorkingDirectory = targetDir });
                    }
                    this.Close();
                };

                MessageBox.Show("Haven 1.0.0 (ODCS Edition) has been successfully installed!\n\nYou can now run 'haven' from any terminal, or launch Haven IDE from the desktop shortcut.", "Installation Successful", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error during installation: " + ex.Message, "Installation Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                installButton.Enabled = true;
            }
        }

        private void UpdateStatus(string message, int progress)
        {
            statusLabel.Text = message;
            progressBar.Value = Math.Min(100, progress);
            Application.DoEvents();
        }

        private static void AddToPath(string targetDir)
        {
            try
            {
                using (RegistryKey envKey = Registry.CurrentUser.OpenSubKey("Environment", true))
                {
                    if (envKey != null)
                    {
                        string currentPath = (envKey.GetValue("Path", "", RegistryValueOptions.DoNotExpandEnvironmentNames) as string) ?? "";
                        if (!currentPath.Contains(targetDir))
                        {
                            string newPath = currentPath.TrimEnd(';') + ";" + targetDir + ";" + Path.Combine(targetDir, "Scripts");
                            envKey.SetValue("Path", newPath, RegistryValueKind.ExpandString);
                            UIntPtr result;
                            SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, UIntPtr.Zero, "Environment", SMTO_ABORTIFHUNG, 5000, out result);
                        }
                    }
                }
            }
            catch { }
        }

        private static void CreateShortcut(string shortcutPath, string target, string args, string iconPath, string description)
        {
            try
            {
                Type shellType = Type.GetTypeFromProgID("WScript.Shell");
                dynamic shell = Activator.CreateInstance(shellType);
                dynamic shortcut = shell.CreateShortcut(shortcutPath);
                shortcut.TargetPath = target;
                if (!string.IsNullOrEmpty(args)) shortcut.Arguments = args;
                if (!string.IsNullOrEmpty(iconPath) && File.Exists(iconPath)) shortcut.IconLocation = iconPath + ",0";
                shortcut.Description = description;
                shortcut.WorkingDirectory = Path.GetDirectoryName(target);
                shortcut.Save();
            }
            catch
            {
                // Fallback using PowerShell
                try
                {
                    string psScript = string.Format("$s=(New-Object -COM WScript.Shell).CreateShortcut('{0}');$s.TargetPath='{1}';$s.Arguments='{2}';$s.WorkingDirectory='{3}';if(Test-Path '{4}'){{$s.IconLocation='{4}'}};$s.Save()",
                        shortcutPath.Replace("'", "''"), target.Replace("'", "''"), args.Replace("'", "''"), Path.GetDirectoryName(target).Replace("'", "''"), iconPath.Replace("'", "''"));
                    Process.Start(new ProcessStartInfo("powershell", "-NoProfile -Command \"" + psScript + "\"") { CreateNoWindow = true, UseShellExecute = false });
                }
                catch { }
            }
        }

        private static void RegisterFileAssociations(string targetDir)
        {
            try
            {
                string havenExe = Path.Combine(targetDir, "haven.exe");
                string havenw = Path.Combine(targetDir, "havenw.exe");
                string icon = Path.Combine(targetDir, "haven.ico");

                using (RegistryKey classes = Registry.CurrentUser.OpenSubKey("Software\\Classes", true))
                {
                    if (classes == null) return;

                    foreach (string ext in new string[] { ".hvn", ".haven" })
                    {
                        using (RegistryKey k = classes.CreateSubKey(ext))
                        {
                            k.SetValue("", "Haven.SourceFile");
                        }
                    }

                    using (RegistryKey progId = classes.CreateSubKey("Haven.SourceFile"))
                    {
                        progId.SetValue("", "Haven Source File (ODCS)");
                        using (RegistryKey iconKey = progId.CreateSubKey("DefaultIcon"))
                        {
                            iconKey.SetValue("", icon);
                        }
                        using (RegistryKey shell = progId.CreateSubKey("shell"))
                        {
                            using (RegistryKey open = shell.CreateSubKey("open"))
                            {
                                open.SetValue("", "Run with Haven");
                                using (RegistryKey cmd = open.CreateSubKey("command"))
                                {
                                    cmd.SetValue("", "\"" + havenExe + "\" \"%1\" %*");
                                }
                            }
                            using (RegistryKey edit = shell.CreateSubKey("edit"))
                            {
                                edit.SetValue("", "Edit with Haven IDE");
                                using (RegistryKey cmd = edit.CreateSubKey("command"))
                                {
                                    cmd.SetValue("", "\"" + havenw + "\" -m idlelib \"%1\"");
                                }
                            }
                        }
                    }
                }
            }
            catch { }
        }

        private static void WriteUninstaller(string targetDir)
        {
            try
            {
                string uninstContent = string.Format(@"@echo off
echo Uninstalling Haven Programming Language...
set ""TARGET_DIR={0}""
set ""DESKTOP=%USERPROFILE%\Desktop""
set ""START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Haven 1.0.0""

if exist ""%DESKTOP%\Haven IDE.lnk"" del ""%DESKTOP%\Haven IDE.lnk""
if exist ""%START_MENU%"" rmdir /s /q ""%START_MENU%""

echo Removing Haven registry associations...
reg delete ""HKCU\Software\Classes\.hvn"" /f >nul 2>&1
reg delete ""HKCU\Software\Classes\.haven"" /f >nul 2>&1
reg delete ""HKCU\Software\Classes\Haven.SourceFile"" /f >nul 2>&1

echo Note: You can delete the installation folder at:
echo %TARGET_DIR%
echo.
echo Haven has been uninstalled successfully.
pause
", targetDir);

                File.WriteAllText(Path.Combine(targetDir, "uninstall.bat"), uninstContent);
            }
            catch { }
        }

        [STAThread]
        public static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new InstallerForm());
        }
    }
}
