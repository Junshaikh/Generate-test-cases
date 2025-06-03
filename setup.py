name: Generate and Run Tests

on:
  workflow_dispatch:
    inputs:
      requirement:
        description: 'Requirement (in plain English)'
        required: true
      squad:
        description: 'Squad name (e.g., squad-auth)'
        required: true
      file_name:
        description: 'Custom file name (optional)'
        required: false
      tag:
        description: 'Priority tag (e.g., P0, P1)'
        required: false
      other_tags:
        description: 'Other tags (e.g., @smoke, @login)'
        required: false

jobs:
  generate-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirement.txt

      - name: Generate test cases
        run: |
          generate-tests \
            --requirement "${{ github.event.inputs.requirement }}" \
            --squad "${{ github.event.inputs.squad }}" \
            --file-name "${{ github.event.inputs.file_name }}" \
            --tag "${{ github.event.inputs.tag }}" \
            --other-tags "${{ github.event.inputs.other_tags }}"

  run-flutter-tests:
    needs: generate-tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.19.0'

      - name: Install dependencies
        run: flutter pub get

      - name: Run Integration Tests
        run: |
          echo "🧪 Running all integration tests..."
          flutter test integration_test/

          TAGS="${{ github.event.inputs.other_tags }}"
          echo "Detected tags: $TAGS"

          if [[ "$TAGS" == *"@login"* ]]; then
            echo "🔐 Running login-related tests"
            flutter test integration_test/login/
          fi

          if [[ "$TAGS" == *"@smoke"* ]]; then
            echo "🔥 Running smoke tests"
            flutter test integration_test/smoke/
          fi
