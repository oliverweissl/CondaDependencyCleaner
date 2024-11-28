import argparse

from ._clean_environment_from_file import clean_environment_from_file


def main() -> None:
    """Main script for cleaning conda environments."""
    parser = argparse.ArgumentParser(
        prog="CondaDependencyCleaner",
        description="Cleans conda environments from transative dependencies.",
        add_help=False,
    )
    parser.add_argument("filename", type=str, help="The conda environment file to clean.")
    parser.add_argument(
        "-nf",
        "--new-filename",
        type=str,
        help="The new conda environment filename.",
        required=False,
    )
    parser.add_argument(
        "--exclude-version",
        help="Allows to exclude version of the dependency.",
        action='store_true'
    )
    parser.add_argument(
        "--exclude-build",
        help="Allows to exclude build of the dependency.",
        action='store_true'
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )

    args = parser.parse_args()
    clean_environment_from_file(
        args.filename,
        args.new_filename,
        exclude_version=args.exclude_version,
        exclude_build=args.exclude_build,
    )


if __name__ == "__main__":
    main()
