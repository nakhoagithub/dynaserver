# Dyna Server
Tác giả: Anh Khoa

### Hướng dẫn cài đặt

I. Môi trường phát triển (dev)

1. Cài đặt docker (Database MongoDB)
- `cd <Thư mục dự án>/docker`
- Chạy mongodb môi trường dev bằng cách chạy lệnh `docker compose -f docker-compose.dev.yaml up -d --build`, các biến môi trường mặc định được cấu hình trong file `docker-compose.dev.yaml`

2. Chạy server trên VSCode
- Cài đặt Python
- Cài đặt môi trường cho Python:
    - `cd <Thư mục dự án>/server`
    - `python -m venv .venv`
    - Kích hoạt môi trường bằng cách chạy file `.venv/Scripts/activate.bat` trên cmd (lưu ý dùng cmd, PowerShell của Window sẽ không có tác dụng trên VSCode)
    - Nếu dùng hệ điều hành Linux hoặc MACOS thì gọi lệnh `source <Đường dẫn tới thư mục>.venv/scripts/activate`
    - Thoát môi trường gọi lệnh `deactivate.bat` hoặc `deactivate` (trên Linux hoặc MACOS)

- Cài đặt thư viện: Sau khi kích hoạt môi trường python, cmd sẽ có dạng như sau `(.venv) D:\<Đường dẫn dự án>`
    - Cài đặt thư viện bằng cách: `pip install -r requirements.txt`

- Chạy server: `python main.py`
    - Sử dụng thư viện `py-mon` giúp cho code dễ hơn, sẽ tự động chạy lại server khi có file .py thay đổi
    - Cài đặt pymon: `pip install py-mon`
    - Chạy `pymon main.py`

II. Môi trường Production

1. Cài docker
2. Chạy server:
- `cd docker`
- `docker compose up -d --build`

### Hướng dẫn viết thêm module

Trong thư mục `<path_to_project>/server/dyna` có thư mục `addons` là thư mục các module cơ bản của server, nó sẽ có các model mặc định về người dùng, phân quyền (role, permission) và menu.

Để viết thêm module mới chỉ cần viết thêm thư mục vào thư mục `<path_to_project>/addons`.

Trong thư mục `<path_to_project>/addons` có sẳn module `example`. Sau đây là giải thích về module và cấu hình một module.

1. Cấu hình:
Mỗi module cần có file `__module__.json` và `__init__.py`

Cần có thư mục `data` nếu cần thêm dữ liệu mặc định cho module, các ví dụ có trong module `example`

`__module__.json` có dạng:
``` json
    {
        "name": "Name: Example",
        "version": "v1.0.0",
        "active": false,
        "data": [
            "example.account.json",
            "example.permission.json",
            "example.role.json"
        ],
        "dependent": [
            "module_name"
        ]
    }
```
Để module hoạt động cần thay đổi `active: true`
`dependent`: là các module phụ thuộc. các module phụ thuộc sẽ được import vào trước.

2. Cách code model (bảng dữ liệu)
- Tạo thư mục `models` bên trong thư mục module và tạo các file .py dành cho model, các ví dụ có trong `example/models/*.py`

3. Cách tạo dữ liệu mặc định
- Tạo file json trong thư mục data, ví dụ `example/data/*.json` file này phải được thêm vào `data` có trong `__module__.json` để dữ liệu được thêm tự động vào cơ sở dữ liệu.

- Ví dụ: `example.account.json` có trường `document` là tên của model, `active: true` cho phép dữ liệu này được thêm vào cơ sở dữ liệu. `data` là danh sách dữ liệu, dạng json, ứng với các trường cấu hình trong model.

- Lưu ý về dữ liệu mặc định:
    - kiểu ngày có dạng json như sau: `{"$date": <int: time unix>}`
    - kiểu objectid: `{"$oid": <str: id>}`

4. Cách viết API (Tìm hiểu thêm về Flask API)
- Tạo thư mục `apis`, tạo các file `*.py` kế thừa DynaResource, ví dụ có trong file `apis/example.py`

5. File `__init__.py` là file import của tất cả các file code model hay api
- Để các api hay các model được hoạt động cần import vào file `__init__.py` của module.

6. Socket IO
- Mặc định socketio được hoạt động, và để kết nối được với nó cần có session. Session được thêm vào header khi kết nối.
- Khi đăng nhập người dùng sẽ nhận được cookie và cookie đó là session để kết nối cho socketio.