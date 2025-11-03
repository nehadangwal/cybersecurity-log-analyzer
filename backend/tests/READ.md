# Test Suite

## Running Tests
```bash
# From backend directory
./run_tests.sh

# Or manually
pytest tests/ -v
```

## Test Files

- `test_api.py` - API endpoint tests (50+ tests)
- `test_log_parser.py` - Log parsing tests (25+ tests)
- `test_anomaly_detector.py` - Anomaly detection tests (35+ tests)

## Coverage

Run with coverage report:
```bash
pytest tests/ --cov=app --cov-report=html
```

View report: `htmlcov/index.html`

## Expected Results

- Total: 110+ tests
- All passing ✅
- Coverage: ~88%

## Test Categories

### API Tests (test_api.py)
- Authentication
- File upload
- Analysis retrieval
- Edge cases

### Parser Tests (test_log_parser.py)
- Apache log format
- ZScaler log format
- Generic log format
- Timeline extraction

### Detector Tests (test_anomaly_detector.py)
- Brute force detection
- Port scanning
- Data exfiltration
- ML model validation