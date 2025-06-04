import argparse

from ._clean_environment_from_file import clean_environment_from_file
from._convert_pip_to_conda import convert_pip_to_conda


def main() -> None:
    """Main script for cleaning conda environments."""
    parser = argparse.ArgumentParser(
        prog="CondaDependencyCleaner",
        description="A helper tool to clean your conda environments and convert pip dependencies to conda.",
        add_help=False,
    )
    subparsers = parser.add_subparsers(dest="command")

    """Parse arguments for cleaning."""
    clean_parser = subparsers.add_parser("clean", help="Clean conda environments from transitive dependencies.")
    clean_parser.add_argument("filename", type=str, help="The conda environment file to clean.")
    clean_parser.add_argument(
        "-nf",
        "--new-filename",
        type=str,
        help="The new conda environment filename.",
        required=False,
    )
    clean_parser.add_argument(
        "--exclude-versions",
        help="Allows to exclude versions of the dependencies.",
        action="store_true",
    )
    clean_parser.add_argument(
        "--exclude-builds",
        help="Allows to exclude builds of the dependencies.",
        action="store_true",
    )
    clean_parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )

    """Parse arguments for converting."""
    convert_parser = subparsers.add_parser("convert", help="Convert pip dependencies to conda dependencies.")
    convert_parser.add_argument("filename", type=str, help="The conda environment file to use for conversion.")
    convert_parser.add_argument(
        "-nf",
        "--new-filename",
        type=str,
        help="The new conda environment filename.",
        required=False,
    )
    convert_parser.add_argument("-c", "--channels", nargs="+", help="The channels to use for conversion, seperated by spaces.")
    convert_parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )

    args = parser.parse_args()
    if args.command == "clean":
        clean_environment_from_file(
            args.filename,
            args.new_filename,
            exclude_versions=args.exclude_versions,
            exclude_builds=args.exclude_builds,
        )
    elif args.command == "convert":
        convert_pip_to_conda(
            args.filename,
            args.new_filename,
            channels=args.channels,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
