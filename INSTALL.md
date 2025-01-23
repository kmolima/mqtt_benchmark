# Installation Instructions
The results presented in the paper, which this artifact accompanies, were derived from the analysis of the benchmark recorded logs. The logs were parsed, processed, and plotted using a Jupyter Notebook. To run the analysis Jupyter notebooks used, you will need a Jupyter Lab installation. Below are the instructions on how to install this software. 

## Linux Command Line
Install JupyterLab with pip:

```bash
pip install jupyterlab
```

More installation options for the command line can be found [here]().

## Jupyter Lab Desktop Application (Windows, Mac, and Linux)
 (Instructions copied from: [https://github.com/jupyterlab/jupyterlab-desktop/blob/master/README.md](https://github.com/jupyterlab/jupyterlab-desktop/blob/master/README.md))

| Windows (10, 11)                                                                                                            | Mac (macOS 10.15+)                                                                                                                            | Linux                                                                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [x64 Installer](https://github.com/jupyterlab/jupyterlab-desktop/releases/latest/download/JupyterLab-Setup-Windows-x64.exe) | [arm64 Installer (Apple silicon)](https://github.com/jupyterlab/jupyterlab-desktop/releases/latest/download/JupyterLab-Setup-macOS-arm64.dmg) | [Snap Store [recommended]](https://snapcraft.io/jupyterlab-desktop)                                                                                     |
|                                                                                                                             | [x64 Installer (Intel chip)](https://github.com/jupyterlab/jupyterlab-desktop/releases/latest/download/JupyterLab-Setup-macOS-x64.dmg)        | [.deb x64 Installer (Debian, Ubuntu)](https://github.com/jupyterlab/jupyterlab-desktop/releases/latest/download/JupyterLab-Setup-Debian-x64.deb)        |
|                                                                                                                             |                                                                                                                                               | [.rpm x64 Installer (Red Hat, Fedora, SUSE)](https://github.com/jupyterlab/jupyterlab-desktop/releases/latest/download/JupyterLab-Setup-Fedora-x64.rpm) |

Additionally, JupyterLab Desktop can be installed on Windows via winget: `winget install jupyterlab`.

If you need to remove a previous JupyterLab Desktop installation, please follow the [uninstall instructions](user-guide.md#uninstalling-jupyterlab-desktop).

Uninstall instructions and more details can be found [here](https://github.com/jupyterlab/jupyterlab-desktop?tab=readme-ov-file#installation).
