# Labtainer DNS Hijacking Labs

Cac bai lab mo phong tan cong va phat hien tan cong DNS/TCP chay tren nen Labtainer (Docker).

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

## 9. tcp-detect-lab (phat hien tan cong TCP)

Bai lab phong thu: sinh vien dong vai chuyen vien SOC, phan tich 3 capture
va bat song mot cu quet cong tren LAN `172.22.0.0/24`.

| Container | IP | Vai tro |
|---|---|---|
| `analyst` | 172.22.0.2 | May tram SOC, co tcpdump + 3 capture |
| `victim` | 172.22.0.3 | May nguoi dung |
| `server` | 172.22.0.4 | Dich vu TCP echo tren cong 9999 |
| `attacker` | 172.22.0.5 | May tan cong, quet cong analyst |

Nhiem vu:
1. Phan tich `01-syn-flood.pcap`: tim IP nguon + so goi SYN.
2. Phan tich `02-rst-injection.pcap`: tim RST gia mao (seq + MAC).
3. Phan tich `03-session-hijack.pcap`: tim du lieu bi chen (seq + payload).
4. Bat song `live-scan.pcap` tren analyst, xac dinh IP may quet.

4 checkwork: `syn_flood_identified`, `rst_injection_identified`,
`session_hijack_identified`, `live_port_scan_identified` (+ `all_passed`).

## Cai dat IModule

Chay trong thu muc `labtainer-student` (thu muc nay da co `./bin` trong PATH):

```bash
cd ~/labtainer/labtainer-student
imodule https://github.com/Versailles1611/labtainer-dns-labs/raw/main/imodules/imodule-tcp-detect-lab.tar
```

URL dang `github.com/<user>/<repo>/raw/main/...` se tu dong redirect sang
`raw.githubusercontent.com`, khong can doi sang dia chi raw dai.

## Chay lab

```bash
cd ~/labtainer/labtainer-student
labtainer tcp-detect-lab        # hoac dns-hijack-lab / dns-hijack-medium
checkwork tcp-detect-lab        # kiem tra giua chung
stoplab tcp-detect-lab          # ket thuc + cham diem
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
