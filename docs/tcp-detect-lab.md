# Kịch bản và hướng dẫn chi tiết — `tcp-detect-lab`

## 1. Thông tin bài lab

| Mục | Nội dung |
|---|---|
| Tên lab | `tcp-detect-lab` |
| Chủ đề | Phát hiện tấn công TCP trên mạng LAN |
| Vai trò | Chuyên viên SOC / điều tra viên mạng |
| Thời lượng | 60–90 phút |
| Công cụ | `tcpdump`, `ip`, `ss`, `nano` |
| Kết quả | `~/answers.txt` trên container `analyst` + `checkwork` |

### Mục tiêu

Sau bài lab, sinh viên có thể:

1. Đọc và phân tích file capture `.pcap` bằng `tcpdump`.
2. Nhận diện **SYN flood** qua số lượng lớn gói SYN không có ACK.
3. Nhận diện **RST injection** qua sự bất thường giữa IP nguồn và MAC nguồn.
4. Nhận diện **session hijacking** qua dữ liệu bị chèn và số sequence.
5. Bắt traffic trực tiếp và phát hiện **SYN port scan**.
6. Ghi lại bằng chứng và kết luận thành báo cáo sự cố.

---

## 2. Kịch bản

Công ty ABC có một mạng LAN nhỏ phục vụ phòng kỹ thuật. Mạng gồm 4 máy:

- Máy trạm của chuyên viên SOC (`analyst`).
- Máy người dùng (`victim`).
- Máy chủ dịch vụ TCP (`server`).
- Một máy đã bị xâm nhập (`attacker`).

Vào đầu giờ làm việc, hệ thống giám sát gửi cảnh báo: có dấu hiệu tấn công TCP trong mạng. Cảm biến đã ghi lại 3 file capture và đặt trên máy `analyst`:

- `01-syn-flood.pcap`
- `02-rst-injection.pcap`
- `03-session-hijack.pcap`

Đồng thời, máy `analyst` đang bị một máy khác quét cổng liên tục. Bạn được giao nhiệm vụ:

1. Phân tích 3 file capture để xác định từng loại tấn công.
2. Bắt traffic trực tiếp trên máy `analyst` để phát hiện nguồn quét cổng.
3. Ghi kết quả vào `~/answers.txt` và chạy `checkwork`.

> Đây là bài lab **phòng thủ**. Không cần thực hiện tấn công; chỉ quan sát, phân tích và kết luận.

---

## 3. Mô hình mạng

LAN: `172.22.0.0/24`

| Host | IP | MAC | Vai trò |
|---|---|---|---|
| `analyst` | 172.22.0.2 | `02:42:ac:16:00:02` | Máy trạm SOC, nơi bạn làm việc |
| `victim` | 172.22.0.3 | `02:42:ac:16:00:03` | Máy người dùng bình thường |
| `server` | 172.22.0.4 | `02:42:ac:16:00:04` | Dịch vụ TCP echo cổng `9999` |
| `attacker` | 172.22.0.5 | `02:42:ac:16:00:05` | Máy bị xâm nhập, đang tấn công |

Điểm quan trọng:

- Trong cùng một LAN, kẻ tấn công có thể **giả mạo IP** nhưng thường vẫn dùng **MAC thật** của máy hắn.
- Vì vậy, khi xem capture với `tcpdump -e`, hãy so sánh:
  - IP nguồn trong header IP.
  - MAC nguồn trong header Ethernet.
- Nếu IP là của `victim` nhưng MAC là của `attacker`, đó là dấu hiệu giả mạo.

---

## 4. Chuẩn bị

### 4.1. Khởi động lab

Trên máy host:

```bash
labtainer tcp-detect-lab
```

Nếu đang có lab khác chạy, dừng lab đó trước:

```bash
stoplab <ten-lab-cu>
```

### 4.2. Mở terminal trên `analyst`

Trong cửa sổ lab, chọn container `analyst`, hoặc dùng:

```bash
docker exec -it -u ubuntu tcp-detect-lab.analyst.student bash
```

Kiểm tra dữ liệu:

```bash
cd ~/captures
ls -l
cat README.txt
```

Bạn sẽ thấy 3 file pcap và file `README.txt` mô tả topology.

### 4.3. Kiểm tra mạng

```bash
ip -4 addr show eth0
ip neigh
ping -c 2 172.22.0.4
```

Mục đích: xác nhận IP/MAC của các host và kết nối tới server.

---

## 5. Phân tích chi tiết

## 5.1. SYN flood — `01-syn-flood.pcap`

### Lý thuyết ngắn

SYN flood là kiểu tấn công gửi rất nhiều gói `SYN` đến một dịch vụ nhưng không hoàn tất bắt tay ba bước. Mỗi gói SYN làm server cấp phát tài nguyên cho một kết nối nửa mở. Khi số lượng quá lớn, server có thể cạn tài nguyên.

Dấu hiệu trong capture:

- Rất nhiều gói `Flags [S]`.
- Không có `Flags [S.]` tương ứng hoặc rất ít.
- Nhiều source port khác nhau, cùng đích đến một cổng dịch vụ.
- Không có ACK hoàn tất.

### Lệnh phân tích

```bash
cd ~/captures

# Xem nhanh 20 gói đầu
tcpdump -nn -r 01-syn-flood.pcap | head -20

# Chỉ lấy các gói SYN không kèm ACK
tcpdump -nn -r 01-syn-flood.pcap \
  'tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack == 0'
```

Đếm số gói SYN:

```bash
tcpdump -nn -r 01-syn-flood.pcap \
  'tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack == 0' \
  2>/dev/null | wc -l
```

### Kết quả mẫu

```text
18:48:32.794572 IP 172.22.0.5.20000 > 172.22.0.4.9999: Flags [S], seq 100000, win 8192, length 0
18:48:32.799572 IP 172.22.0.5.20001 > 172.22.0.4.9999: Flags [S], seq 107919, win 8192, length 0
18:48:32.804572 IP 172.22.0.5.20002 > 172.22.0.4.9999: Flags [S], seq 115838, win 8192, length 0
```

Số gói SYN đếm được: `120`.

### Cách xác định IP nguồn

Có thể dùng:

```bash
tcpdump -nn -r 01-syn-flood.pcap \
  'tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack == 0' \
  2>/dev/null | awk '{print $3}' | sed 's/\.[0-9]*$//' | sort | uniq -c
```

Kết quả cho thấy toàn bộ gói SYN đến từ `172.22.0.5`.

### Ghi kết quả

```text
SYN_FLOOD_SRC=172.22.0.5
SYN_COUNT=120
```

---

## 5.2. RST injection — `02-rst-injection.pcap`

### Lý thuyết ngắn

TCP dùng gói `RST` để đóng một kết nối. Nếu kẻ tấn công biết đủ thông tin của phiên (IP, port, sequence number), hắn có thể gửi một RST giả mạo để phá phiên.

Trong cùng LAN, kẻ tấn công thường:

- Giả mạo **IP nguồn** thành IP của nạn nhân.
- Nhưng vẫn dùng **MAC thật** của máy hắn.

Đây là điểm mấu chốt để phát hiện.

### Lệnh phân tích

```bash
cd ~/captures

# Chỉ xem các gói RST, kèm MAC (-e) và sequence tuyệt đối (-S)
tcpdump -nn -e -S -r 02-rst-injection.pcap \
  'tcp[tcpflags] & tcp-rst != 0'
```

Xem toàn bộ phiên để hiểu ngữ cảnh:

```bash
tcpdump -nn -e -S -r 02-rst-injection.pcap
```

### Kết quả mẫu

```text
18:48:32.934572 02:42:ac:16:00:05 > 02:42:ac:16:00:04,
ethertype IPv4 (0x0800), length 54:
172.22.0.3.40000 > 172.22.0.4.9999: Flags [R], seq 1007, win 8192, length 0
```

Phân tích:

| Trường | Giá trị | Ý nghĩa |
|---|---|---|
| MAC nguồn | `02:42:ac:16:00:05` | MAC của `attacker` |
| IP nguồn | `172.22.0.3` | IP của `victim` |
| Cổng nguồn | `40000` | Cổng của phiên victim |
| Cổng đích | `9999` | Dịch vụ server |
| Flags | `[R]` | RST |
| Sequence | `1007` | Nằm đúng cửa sổ phiên victim |

Kết luận: gói RST mang IP của victim nhưng MAC của attacker → **RST bị giả mạo**.

### Ghi kết quả

```text
RST_SEQ=1007
RST_SRC_MAC=02:42:ac:16:00:05
```

---

## 5.3. Session hijacking — `03-session-hijack.pcap`

### Lý thuyết ngắn

Trong session hijacking, kẻ tấn công chen dữ liệu vào một phiên TCP đã thiết lập. Hắn dùng:

- IP và port của nạn nhân.
- Sequence number tiếp theo của nạn nhân.
- MAC thật của hắn.

Nếu server chấp nhận, dữ liệu của kẻ tấn công được xử lý như dữ liệu hợp lệ của nạn nhân.

### Lệnh phân tích

```bash
cd ~/captures

# Xem toàn bộ phiên, kèm MAC, sequence và payload ASCII (-A)
tcpdump -nn -e -S -A -r 03-session-hijack.pcap 'tcp port 9999'
```

### Kết quả mẫu

```text
18:48:32.854572 02:42:ac:16:00:03 > 02:42:ac:16:00:04, ... 
172.22.0.3.40001 > 172.22.0.4.9999: Flags [P.], seq 7001:7007, ack 9001, length 6
...
HELLO

18:48:32.934572 02:42:ac:16:00:05 > 02:42:ac:16:00:04, ...
172.22.0.3.40001 > 172.22.0.4.9999: Flags [P.], seq 7007:7016, ack 9011, length 9
...
HIJACKED

18:48:32.954572 02:42:ac:16:00:04 > 02:42:ac:16:00:03, ...
172.22.0.4.9999 > 172.22.0.3.40001: Flags [.], ack 7016, length 0

18:48:32.974572 02:42:ac:16:00:04 > 02:42:ac:16:00:03, ...
172.22.0.4.9999 > 172.22.0.3.40001: Flags [P.], seq 9011:9024, ack 7016, length 13
...
ACK:HIJACKED
```

Phân tích:

- Gói `HELLO` hợp lệ do victim gửi: MAC `...:03`, seq `7001:7007`.
- Gói bất thường:
  - MAC nguồn `02:42:ac:16:00:05` (attacker).
  - IP nguồn `172.22.0.3` (victim).
  - Port nguồn `40001` (victim).
  - Sequence `7007:7016` — tiếp ngay sau `HELLO`.
  - Payload `HIJACKED`.
- Server đã ACK tới `7016` và trả về `ACK:HIJACKED` → dữ liệu bị chèn đã được chấp nhận.
- Victim gửi RST ở cuối vì nhận dữ liệu không mong đợi.

### Ghi kết quả

```text
HIJACK_SEQ=7007
HIJACK_PAYLOAD=HIJACKED
```

---

## 5.4. SYN port scan — bắt traffic trực tiếp

### Lý thuyết ngắn

SYN scan gửi gói SYN đến nhiều cổng khác nhau trên cùng một host để xem cổng nào mở. Dấu hiệu:

- Một IP nguồn.
- Nhiều cổng đích khác nhau.
- Phần lớn là SYN, không hoàn tất bắt tay.
- Thời gian đến rất gần nhau.

Trong lab, máy `attacker` quét các cổng `1–100` của `analyst` lặp lại khoảng mỗi 8 giây.

### Bắt traffic

Trên `analyst`:

```bash
sudo tcpdump -Z root -U -nn -i eth0 -w ~/live-scan.pcap \
  'tcp[tcpflags] & tcp-syn != 0'
```

Đợi khoảng **15 giây**, sau đó nhấn `Ctrl+C`.

> Phải dùng `-Z root`. Nếu không, `tcpdump` có thể báo:
> `tcpdump: Couldn't change ownership of savefile`

### Kiểm tra capture

```bash
sudo tcpdump -nn -r ~/live-scan.pcap | head -20
```

Kết quả mẫu:

```text
02:02:35.983390 IP 172.22.0.5.46518 > 172.22.0.2.79: Flags [S], seq 1664889017, win 8192, length 0
02:02:36.064561 IP 172.22.0.5.23870 > 172.22.0.2.80: Flags [S], seq 163355356, win 8192, length 0
02:02:36.147498 IP 172.22.0.5.36316 > 172.22.0.2.81: Flags [S], seq 475617592, win 8192, length 0
```

Đếm số cổng đích khác nhau:

```bash
sudo tcpdump -nn -r ~/live-scan.pcap 'src host 172.22.0.5' \
  | awk '{print $5}' | sed 's/.*\.//' | tr -d ':' \
  | sort -n | uniq | wc -l
```

Kết quả thường là `100` nếu bắt trọn một vòng quét; chỉ cần **≥ 20** là đủ kết luận có quét cổng.

Nếu chưa thấy gói nào:

- Đợi 10 giây rồi bắt lại.
- Kiểm tra container attacker còn chạy không:
  ```bash
  docker ps | grep attacker
  ```
- Kiểm tra tiến trình quét trong container attacker:
  ```bash
  docker exec -u ubuntu tcp-detect-lab.attacker.student ps aux | grep scan
  ```

### Ghi kết quả

```text
LIVE_SCAN_SRC=172.22.0.5
```

---

## 6. Ghi báo cáo và chấm điểm

### 6.1. Điền `answers.txt`

Trên `analyst`:

```bash
nano ~/answers.txt
```

Điền đúng định dạng `KEY=value`, không thêm khoảng trắng quanh dấu `=`:

```text
SYN_FLOOD_SRC=172.22.0.5
SYN_COUNT=120
RST_SEQ=1007
RST_SRC_MAC=02:42:ac:16:00:05
HIJACK_SEQ=7007
HIJACK_PAYLOAD=HIJACKED
LIVE_SCAN_SRC=172.22.0.5
```

Kiểm tra lại:

```bash
cat ~/answers.txt
```

### 6.2. Chấm điểm

Trên máy host:

```bash
checkwork tcp-detect-lab
```

Kết quả mong đợi:

```text
Y - syn_flood_identified
Y - rst_injection_identified
Y - session_hijack_identified
Y - live_port_scan_identified
Y - all_passed
```

### 6.3. Kết thúc

```bash
stoplab tcp-detect-lab
```

---

## 7. Mẫu báo cáo sự cố

Có thể dùng mẫu sau để trình bày kết quả:

```text
BÁO CÁO PHÂN TÍCH SỰ CỐ TCP
===========================

Người phân tích:
Thời gian:
Mạng: 172.22.0.0/24

1. Sự kiện SYN flood
   - Nguồn:
   - Số gói SYN:
   - Bằng chứng:
   - Kết luận:

2. Sự kiện RST injection
   - IP bị giả mạo:
   - MAC thật của kẻ tấn công:
   - Sequence của RST:
   - Bằng chứng:
   - Kết luận:

3. Sự kiện session hijacking
   - Phiên bị ảnh hưởng:
   - Sequence bị chèn:
   - Payload:
   - Bằng chứng:
   - Kết luận:

4. Sự kiện quét cổng
   - IP nguồn:
   - Số cổng đích:
   - Thời gian bắt:
   - Bằng chứng:
   - Kết luận:

Đề xuất xử lý:
- Cách ly máy bị xâm nhập.
- Kiểm tra log server.
- Bật ingress filtering / chống giả mạo IP.
- Giám sát các gói RST bất thường.
```

---

## 8. Đáp án tham khảo (dành cho giảng viên)

| Biến | Giá trị | Giải thích |
|---|---|---|
| `SYN_FLOOD_SRC` | `172.22.0.5` | IP nguồn của 120 gói SYN |
| `SYN_COUNT` | `120` | Số gói SYN không ACK trong capture |
| `RST_SEQ` | `1007` | Sequence của gói RST giả mạo |
| `RST_SRC_MAC` | `02:42:ac:16:00:05` | MAC attacker trong gói RST |
| `HIJACK_SEQ` | `7007` | Sequence của gói chứa `HIJACKED` |
| `HIJACK_PAYLOAD` | `HIJACKED` | Dữ liệu bị chèn |
| `LIVE_SCAN_SRC` | `172.22.0.5` | IP nguồn của live SYN scan |

---

## 9. Câu hỏi thảo luận

1. Vì sao kẻ tấn công có thể giả mạo IP nguồn nhưng khó giả mạo MAC nguồn trong cùng LAN?
2. Sự khác nhau giữa SYN flood và SYN port scan là gì?
3. Làm thế nào để phát hiện RST injection nếu capture không có thông tin MAC?
4. Vì sao server vẫn ACK dữ liệu `HIJACKED` trong kịch bản session hijacking?
5. Nêu một số biện pháp phòng chống:
   - SYN flood.
   - RST injection.
   - Session hijacking.
   - Port scan.
6. Nếu triển khai IDS/IPS, nên đặt cảm biến ở đâu để phát hiện các sự kiện trên?

---

## 10. Xử lý sự cố

### `tcpdump: Couldn't change ownership of savefile`

Dùng `-Z root` khi ghi file bằng `sudo`:

```bash
sudo tcpdump -Z root -U -nn -i eth0 -w ~/live-scan.pcap 'tcp[tcpflags] & tcp-syn != 0'
```

### `checkwork` báo sai dù đã điền đáp án

Kiểm tra:

```bash
cat ~/answers.txt
```

Các lỗi thường gặp:

- Có khoảng trắng quanh dấu `=`.
- Sai chữ hoa/chữ thường.
- Thiếu dòng.
- Dùng sai địa chỉ MAC (ví dụ dùng MAC của victim thay vì attacker).

### `live_port_scan_identified` vẫn đỏ

- Đảm bảo file `~/live-scan.pcap` tồn tại:
  ```bash
  ls -l ~/live-scan.pcap
  ```
- Đảm bảo bắt đủ lâu (≥ 15 giây).
- Kiểm tra capture có gói SYN từ `172.22.0.5`:
  ```bash
  sudo tcpdump -nn -r ~/live-scan.pcap 'src host 172.22.0.5'
  ```
- Nếu chưa có, đợi 10 giây rồi bắt lại.

### `imodule: command not found`

```bash
cd ~/labtainer/labtainer-student
source ~/.bashrc
```

Hoặc dùng đường dẫn đầy đủ một lần:

```bash
~/labtainer/trunk/scripts/labtainer-student/bin/imodule <url>
```

### `Already exists! Not creating lan subnet`

Đang có lab khác giữ mạng `lan`. Dừng lab cũ:

```bash
stoplab <ten-lab-cu>
```

### `Could not find image for ...`

Xóa cache `start.config` cũ của lab rồi chạy lại:

```bash
rm -rf ~/labtainer/trunk/scripts/labtainer-student/.tmp/tcp-detect-lab
labtainer tcp-detect-lab
```

---

## 11. Checklist hoàn thành

- [ ] Đã xem `~/captures/README.txt`.
- [ ] Đã xác định SYN flood: IP nguồn + số gói SYN.
- [ ] Đã xác định RST injection: sequence + MAC attacker.
- [ ] Đã xác định session hijacking: sequence + payload.
- [ ] Đã bắt `~/live-scan.pcap` và xác định IP quét.
- [ ] Đã điền đủ `~/answers.txt`.
- [ ] `checkwork tcp-detect-lab` hiện đủ 5 dòng `Y`.
- [ ] Đã chạy `stoplab tcp-detect-lab`.
