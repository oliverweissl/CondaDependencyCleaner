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
        "--exclude-versions",
        help="Allows to exclude versions of the dependencies.",
        action="store_true",
    )
    parser.add_argument(
        "--exclude-builds",
        help="Allows to exclude builds of the dependencies.",
        action="store_true",
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
        exclude_versions=args.exclude_versions,
        exclude_builds=args.exclude_builds,
    )


if __name__ == "__main__":
    main()
