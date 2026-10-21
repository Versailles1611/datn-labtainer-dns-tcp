# Labtainer DNS Hijacking Labs

Hai bai lab mo phong tan cong DNS Hijacking / Pharming chay tren nen Labtainer (Docker).

## 1. dns-hijack-lab (muc do: trung binh)

Mo phong chuyen huong truy van DNS cua nan nhan sang rogue DNS server.

| Container | IP | Vai tro |
|---|---|---|
| `victim` | 172.20.0.2 | Nan nhan (`nameserver 172.20.0.3` ban dau) |
| `dns-server` | 172.20.0.3 | DNS hop le, zone `lab.local` (`portal A 172.20.0.3`) |
| `attacker` | 172.20.0.4 | Rogue DNS (BIND9 san, chua cau hinh pharming) |

Nhiem vu sinh vien:
1. Tren `attacker`: sua `/etc/bind/db.lab.local` thanh `portal IN A 172.20.0.99`, `service bind9 reload`.
2. Tren `victim`: doi `/etc/resolv.conf` thanh `nameserver 172.20.0.4`.
3. Kiem chung: `dig portal.lab.local +short` phai ra `172.20.0.99`.

4 checkwork: `cw_resolver`, `cw_rogue_answer`, `cw_rogue_query`, `cw_rogue_conf`.

## 2. dns-hijack-medium (SEED Local DNS Attack)

Bai lab SEED, 4 container: `user` (192.168.0.100), `apollo-dns` (192.168.0.10, BIND9,
`forward only` qua gateway, `dnssec-validation no`), `gateway` (192.168.0.1, dnsmasq),
`attacker` (192.168.0.200, netwox + tcpdump).

4 task theo giao trinh SEED:
1. Sua `/etc/hosts` tren user: `1.2.3.4 www.example.com`.
2. Spoof truc tiep reply toi user (netwox 80 + netwox 105, filter `src host 192.168.0.100`), luu pcap.
3. Cache poisoning Apollo (ARP poison Apollo<->gateway, netwox 105 filter `src host 192.168.0.10`,
   fake `www.chase.com A 10.99.0.99`), luu `/home/ubuntu/spoof.pcapng`.
4. Verify `dig www.chase.com` tren user tra ve `10.99.0.99` va cache Apollo co ban ghi gia.

4 checkwork: `cw_task1_hosts`, `cw_task2_pcap`, `cw_task3_cache`, `cw_task4_userfake`.

## Chay lab

```bash
cd ~/labtainer/labtainer-student
labtainer dns-hijack-lab        # hoac dns-hijack-medium
checkwork dns-hijack-medium     # kiem tra giua chung
stoplab dns-hijack-medium       # ket thuc + cham diem
```

Rebuild image sau khi sua lab:

```bash
rebuild dns-hijack-medium -f -L -C apollo-dns
```

## Xu ly su co

### `Remote image ... is lacking a base version`

Labtainer tu choi image tren Docker Hub neu image thieu label `base`. Khi rebuild/push
image moi, chay lai:

```bash
./distrib/add-base-labels.sh haiyen1102
```

Script se them label `base=labtainers/labtainer.base2.<id>` cho tat ca image
`<lab>.<container>.student` cua cac lab trong repo va push lai len Docker Hub.

### Sau khi cap nhat lab: `Could not find image for ...`

Labtainer cache ban copy cua `start.config` tai
`~/labtainer/trunk/scripts/labtainer-student/.tmp/<lab>/start.config`.
Neu lab da tung duoc chay bang phien ban cu (vi du truoc khi them `REGISTRY`),
ban copy nay se duoc dung lai va co the sai registry. Xoa cache cua lab do:

```bash
rm -rf ~/labtainer/trunk/scripts/labtainer-student/.tmp/<lab>
```

roi chay lai `labtainer <lab>`.
