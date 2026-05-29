# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# Stage 1 – build RTKLIB EX rnx2rtkp from the pinned submodule
#
# RTKLIB source: git submodule rtklib/ (rtklibexplorer/RTKLIB, branch demo5)
# Commit is pinned in .gitmodules — override with --build-arg to test others.
# ---------------------------------------------------------------------------
FROM debian:bookworm-slim AS rtklib-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy only the RTKLIB submodule source (already checked out on the host)
COPY rtklib/ /rtklib/

WORKDIR /rtklib/app/consapp/rnx2rtkp/gcc
# -lrt is Linux-only; override LDLIBS to drop -lgfortran (no IERS model needed)
RUN make LDLIBS="-lm"

# ---------------------------------------------------------------------------
# Stage 2 – Python runtime + project
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# System dependencies for contextily (requests, PIL) and pyproj (PROJ)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libproj-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy compiled rnx2rtkp binary from builder stage
COPY --from=rtklib-builder /rtklib/app/consapp/rnx2rtkp/gcc/rnx2rtkp \
     /app/examples/experiments/rnx2rtkp
RUN chmod +x /app/examples/experiments/rnx2rtkp

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source (raw_data and outputs are mounted as volumes)
COPY gnsspos/      gnsspos/
COPY examples/experiments/ examples/experiments/
COPY README.md .

# Default: run the master plot script
CMD ["python", "examples/experiments/plot.py"]
