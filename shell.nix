{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = with pkgs; [
    python313
    uv
    sqlite
    curl
  ];

  shellHook = ''
    echo "Edge service dev shell"
    echo "Run: uv sync"
    echo "Run: uv run python app.py"
  '';
}
