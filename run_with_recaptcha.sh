#!/bin/bash

# Set reCAPTCHA environment variables
# Using Google's test keys for development (always pass verification)
export RECAPTCHA_SITE_KEY="6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
export RECAPTCHA_SECRET_KEY="6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"

# Activate conda environment and run the app
conda activate webapp
python run.py

