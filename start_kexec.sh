kexec -p /boot/vmlinuz-linux --initrd=/boot/initramfs-linux.img --append="root=/dev/nvme0n1p3 single irqpoll maxcpus=1 reset_devices"
