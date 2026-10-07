# SIGNAL RESCUE — Web Edition

Interactive browser version of the ARES-7 Signals & Systems rescue game.

## Local run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository named `signal-rescue-ares7`.
2. Upload everything in this folder to the repository.
3. Go to https://share.streamlit.io and sign in with GitHub.
4. Choose **Create app** → **I have an app**.
5. Select your repository, branch `main`, and file:
   `streamlit_app.py`
6. Choose a custom app URL such as `signal-rescue-ares7`.
7. Click Deploy.

The result will be a shareable URL under `streamlit.app`.


## Streamlit Cloud image fix

The artwork is now resolved relative to `streamlit_app.py` and loaded through Pillow, so deployment does not depend on the Streamlit working directory. Keep `assets/retro_space_art.png` at that exact repository path.
