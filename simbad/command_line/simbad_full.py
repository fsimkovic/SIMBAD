#!/usr/bin/env python

from __future__ import print_function

__author__ = "Adam Simpkin, and Felix Simkovic"
__contributing_authors__ = "Jens Thomas, and Ronan Keegan"
__credits__ = "Daniel Rigden, William Shepard, Charles Ballard, Villi Uski, and Andrey Lebedev"
__date__ = "05 May 2017"
__email__ = "hlasimpk@liv.ac.uk"
__version__ = "0.1"

import argparse
import os
import sys

from pyjob.misc import StopWatch

import simbad.command_line
import simbad.exit
import simbad.util.pyrvapi_results

logger = None


def simbad_argparse():
    """Create the argparse options"""
    p = argparse.ArgumentParser(
        description="SIMBAD: Sequence Independent Molecular replacement Based on Available Database",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    simbad.command_line._argparse_core_options(p)
    simbad.command_line._argparse_job_submission_options(p)
    simbad.command_line._argparse_contaminant_options(p)
    simbad.command_line._argparse_morda_options(p)
    simbad.command_line._argparse_lattice_options(p)
    simbad.command_line._argparse_rot_options(p)
    simbad.command_line._argparse_mr_options(p)
    simbad.command_line._argparse_mtz_options(p)
    p.add_argument('mtz', help="The path to the input mtz file")
    return p


def main():
    """Main SIMBAD routine"""
    args = simbad_argparse().parse_args()

    args.work_dir = simbad.command_line.get_work_dir(
        args.run_dir, work_dir=args.work_dir, ccp4_jobid=args.ccp4_jobid
    )

    if not os.path.isfile(args.amore_exe):
        raise OSError("amore executable not found")

    # Account for the fact that argparse can't take bool
    if str(args.early_term).lower() == 'false':
        args.early_term = False

    if str(args.no_gui).lower() == "false":
        args.no_gui = False

    # Logger setup
    global logger
    log = os.path.join(args.work_dir, 'simbad.log')
    debug_log = os.path.join(args.work_dir, 'debug.log')
    logger = simbad.command_line.setup_logging(level=args.debug_lvl, logfile=log,
                                               debug_logfile=debug_log)

    #GUI setup
    gui = simbad.util.pyrvapi_results.SimbadOutput(args.work_dir)
    gui.display_results(args.rvapi_document, args.webserver_uri,
                        args.no_gui, log, summary=False)

    # Print some nice information
    simbad.command_line.print_header()
    logger.info("Running in directory: %s\n", args.work_dir)

    # Start taking time
    stopwatch = StopWatch()
    stopwatch.start()

    # Let's start searching old boyo
    end_of_cycle, solution_found = False, False
    while not (solution_found or end_of_cycle):
        # =====================================================================================
        # Perform the lattice search
        solution_found = simbad.command_line._simbad_lattice_search(args)
        logger.info("Lattice search completed in %d days, %d hours, %d minutes, and %d seconds",
                    *stopwatch.lap.time_pretty)

        if solution_found and args.early_term:
            logger.info(
                "Lucky you! SIMBAD worked its charm and found a lattice match for you.")
            continue
        elif solution_found and not args.early_term:
            logger.info(
                "SIMBAD thinks it has found a solution however early_term set to %s, continuing to contaminant search", args.early_term)
        else:
            logger.info("No results found - lattice search was unsuccessful")

        gui.display_results(args.rvapi_document, args.webserver_uri,
                            args.no_gui, log, summary=False)

        # =====================================================================================
        # Perform the contaminant search
        solution_found = simbad.command_line._simbad_contaminant_search(args)
        logger.info("Contaminant search completed in %d days, %d hours, %d minutes, and %d seconds",
                    *stopwatch.lap.time_pretty)

        if solution_found and args.early_term:
            logger.info(
                "Check you out, crystallizing contaminants! But don't worry, SIMBAD figured it out and found a solution.")
            continue
        elif solution_found and not args.early_term:
            logger.info(
                "SIMBAD thinks it has found a solution however early_term set to %s, continuing to morda search", args.early_term)
        else:
            logger.info(
                "No results found - contaminant search was unsuccessful")

        gui.display_results(args.rvapi_document, args.webserver_uri,
                            args.no_gui, log, summary=False)

        # =====================================================================================
        # Perform the morda search
        solution_found = simbad.command_line._simbad_morda_search(args)
        logger.info("Full MoRDa domain search completed in %d days, %d hours, %d minutes, and %d seconds",
                    *stopwatch.lap.time_pretty)
        if solution_found:
            logger.info("... and SIMBAD worked once again. Get in!")
            continue
        else:
            logger.info("No results found - full search was unsuccessful")

        gui.display_results(args.rvapi_document, args.webserver_uri,
                            args.no_gui, log, summary=False)

        # =====================================================================================
        # Make sure we only run the loop once for now
        end_of_cycle = True

    # Calculate and display the runtime in hours
    stopwatch.stop()
    logger.info("All processing completed in %d days, %d hours, %d minutes, and %d seconds",
                *stopwatch.time_pretty)

    # Output summary in gui
    gui.display_results(args.rvapi_document, args.webserver_uri,
                        args.no_gui, log, summary=True)
    if args.rvapi_document:
        gui.save_document(args.rvapi_document)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        simbad.exit.exit_error(*sys.exc_info())
