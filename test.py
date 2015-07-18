from radar2gif import radar_to_gif


def test_palette(max_number_of_frames):
    """Runs radar to gif safely, not publishing results and providing a means
    to shorten the process by providing a constraint for the number of images
    processed"""

    radar_to_gif(tweet=False, max_number_of_frames=max_number_of_frames)

test_palette(3)
