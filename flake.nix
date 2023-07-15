{
  description = "bindings generation dev env";

  inputs = { nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05"; };

  outputs = { self, nixpkgs }:
    let
      allSystems = [
        "x86_64-linux" # AMD/Intel Linux
        "x86_64-darwin" # AMD/Intel macOS
        "aarch64-linux" # ARM Linux
        "aarch64-darwin" # ARM macOS
      ];

      forAllSystems = fn:
        nixpkgs.lib.genAttrs allSystems
        (system: fn { pkgs = import nixpkgs { inherit system; }; });

      rev = "${self.lastModifiedDate}";

    in {
      # used when calling `nix fmt <path/to/flake.nix>`
      formatter = forAllSystems ({ pkgs }: pkgs.nixfmt);

      # nix develop <flake-ref>#<name>
      # -- 
      # $ nix develop <flake-ref>#blue
      # $ nix develop <flake-ref>#yellow
      devShells = forAllSystems ({ pkgs }:
        let python = pkgs.python311Packages;
        in {
          default = pkgs.mkShell {
            name = "nixdev";
            nativeBuildInputs = (with pkgs.python311Packages; [
              python-lsp-server
              pyls-isort
              pylsp-mypy
              pytest
              black
              sphinx
            ]);
          };
        });

      # nix run|build <flake-ref>#<pkg-name>
      # -- 
      # $ nix run <flake-ref>#hello
      # $ nix run <flake-ref>#cowsay
      packages = forAllSystems ({ pkgs }:
        let python = pkgs.python311Packages;
        in rec {
          gcgen = (python.buildPythonPackage rec {
            pname = "gcgen";
            version = rev;
            src = ./.;
            doCheck = true;
            propagatedBuildInputs = [ ];
            checkInputs = (with python; [ pytest ]);
            checkPhase = ''
              TERM=unknown python -m pytest
            '';
            meta = with pkgs.lib; {
              description = "a general code generator";
              homepage = "https://jwdevantier.github.io/gcgen/";
              license = licenses.mit;
            };
          });
        });
    };
}
