from telegram.ext import ApplicationBuilder

# Mock application run_polling just to see if arguments are accepted (doesn't start loop)
try:
    app = ApplicationBuilder().token("123:abc").build()

    # We inspect the method signature or call it but break immediately
    import inspect
    sig = inspect.signature(app.run_polling)
    print("Signature:", sig)

    # Check if run_polling accepts read_timeout
    if 'read_timeout' in sig.parameters:
        print("read_timeout is VALID")
    else:
        print("read_timeout is INVALID (Correct for v20+)")

except Exception as e:
    print(e)
