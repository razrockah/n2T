"""Export the slab model and open it in the openmc-plotter GUI."""
import argparse
import subprocess

from slab_model import slab_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-m', '--breeder', choices=['pbli', 'li', 'flibe'], default='pbli',
                        help='breeder material (default: pbli)')
    parser.add_argument('-e', '--enrichment', type=float, default=90,
                        help='Li-6 enrichment in atom percent (default: 90)')
    parser.add_argument('-o', '--output', default='model.xml',
                        help='output XML path (default: model.xml)')
    args = parser.parse_args()

    slab_model(args.breeder, args.enrichment).export_to_model_xml(args.output)
    subprocess.run(['openmc-plotter', args.output])


if __name__ == '__main__':
    main()
