# Using usbipd-win to access serial port from WSL instance

Install usbipd-win from [GitHub Repo.](https://github.com/dorssel/usbipd-win)

### List USB Devices (PowerShell Administrator)

```shell
usbipd list
```

### Bind the USB to shared buses

```shell
usbipd bind -b <BUS_ID>
```
```shell
usbipd bind -i <VID>:<PID>
```

### Attach the USB to WSL

```shell
usbipd attach -w -a -b <BUS_ID>
```
```shell
usbipd attach -w -a -i <VID>:<PID>
```

### Keyword Arguments

- `-a` Auto attach
- `-w` WSL
- `-i` Hardware ID
- `-b` Bus ID
