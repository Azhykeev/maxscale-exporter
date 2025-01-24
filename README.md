
# MaxScale Exporter

The MaxScale Exporter is a Prometheus-compatible service that connects to multiple MaxScale pods, fetches metrics, and exposes them for monitoring purposes.

## Features
- Connects to multiple MaxScale pods.
- Collects metrics like service availability, queries processed, current connections, and more.
- Tracks connections by service and server.
- Records the MaxScale version running on each pod.
- Exposes metrics at the `/metrics` endpoint in Prometheus format.
- Configurable MaxScale pod addresses through environment variables.

## Project Structure
```plaintext
.
├── Dockerfile           # Dockerfile to build the exporter image
├── README.md            # Project documentation
├── maxscale_exporter.py # Main Python script for the exporter
├── requirements.txt     # Python dependencies
└── LICENSE              # License file (add your license here)
```

## Requirements
- Python 3.9+
- Prometheus

## Installation
### Clone the Repository
```bash
git clone https://github.com/yourusername/maxscale-exporter.git
cd maxscale-exporter
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Configuration
Set the `MAXSCALE_PODS` environment variable to define the MaxScale pods:
```bash
export MAXSCALE_PODS="maxscale-pod-1,maxscale-pod-2,maxscale-pod-3"
```

## Usage
### Run Locally
```bash
python maxscale_exporter.py
```
Access metrics at `http://localhost:8000/metrics`.

### Run with Docker
#### Build the Docker Image
On Windows, ensure Docker Desktop is installed and running.
```powershell
docker build -t maxscale-exporter .
```

#### Run the Docker Container
```powershell
docker run -e MAXSCALE_PODS="maxscale-pod-1,maxscale-pod-2,maxscale-pod-3" -p 8000:8000 maxscale-exporter
```

#### Verify the Docker Image
You can check the running container and logs:
```powershell
docker ps
```
```powershell
docker logs <container-id>
```

### Prometheus Configuration
Add the exporter to your Prometheus configuration:
```yaml
scrape_configs:
  - job_name: 'maxscale-exporter'
    static_configs:
      - targets: ['<exporter-host>:8000']
```

## Metrics
The exporter exposes the following metrics:

| Metric Name                 | Description                                    | Labels             |
|-----------------------------|------------------------------------------------|--------------------|
| `maxscale_up`               | Service availability (1 = up, 0 = down)       | `pod`             |
| `maxscale_queries`          | Number of queries processed                   | `pod`             |
| `maxscale_connections`      | Current connections                           | `pod`             |
| `maxscale_sessions`         | Active sessions on MaxScale                   | `pod`             |
| `maxscale_latency`          | Average query latency (ms)                    | `pod`             |
| `maxscale_errors`           | Number of errors encountered                  | `pod`             |
| `maxscale_service_connections` | Connections per service                     | `pod`, `service`  |
| `maxscale_server_connections`  | Connections per server                      | `pod`, `server`   |
| `maxscale_version`          | MaxScale version                              | `pod`, `version`  |

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [aiohttp Library](https://github.com/aio-libs/aiohttp)
- [MaxScale Documentation](https://mariadb.com/docs/maxscale/)

## Support
If you encounter any issues, please open an issue in this repository.
