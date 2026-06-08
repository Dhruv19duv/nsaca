FROM rust:1.75-slim as builder

WORKDIR /app

# Copy manifests
COPY Cargo.toml Cargo.lock* ./
COPY rust/Cargo.toml rust/Cargo.toml

# Build dependencies (cached layer)
RUN mkdir -p rust/src && echo "fn main() {}" > rust/src/main.rs && \
    cargo build --release 2>/dev/null || true

# Copy source
COPY rust/ ./rust/

# Build the actual binary
RUN cargo build --release --manifest-path rust/Cargo.toml

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/rust/target/release/nsaca_dsa /usr/local/bin/nsaca_dsa

CMD ["nsaca_dsa"]
