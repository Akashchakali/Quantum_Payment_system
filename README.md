# QuantumPay Shield

QuantumPay Shield is a Streamlit based final-semester prototype for a quantum cryptography secured online payment system. It simulates BB84 Quantum Key Distribution, calculates QBER, detects eavesdropping, encrypts payment payloads for demonstration, and authorizes or blocks transactions.

## Features

- Dashboard with payment app style navigation
- Password protected payment and balance enquiry
- Pay to saved contacts
- Pay to custom account
- Pay to self account
- Two successful and two failed demo payment outcomes
- BB84 quantum key generation simulation
- QBER based eavesdropping detection
- Animated payment success and failure screens
- Transaction history
- QBER, balance, amount, and status graph analysis
- QR code generation
- Quantum themed animated background

## Demo Password

```text
quantum123
```

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run app.py
```

## Demo Flow

1. Open the app.
2. Go to Make Payment.
3. Choose a saved contact.
4. Enter password `quantum123`.
5. Make the payments.
6. The first payment will succeed.
7. The second payment will fails because QBER detects eavesdropping.
8. Open Transaction History and Graph Analysis to explain the results.
