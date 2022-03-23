from features.models import FeatureSegment, FeatureState
from features.versioning.models import EnvironmentFeatureVersion
from segments.models import Segment


def test_create_environment_feature_version(environment, feature):
    # Given
    version = EnvironmentFeatureVersion(environment=environment, feature=feature)

    segment = Segment.objects.create(project=environment.project)
    feature_segment = FeatureSegment.objects.create(
        segment=segment, feature=feature, environment=environment
    )
    FeatureState.objects.create(
        environment=environment, feature=feature, feature_segment=feature_segment
    )

    # When
    version.save()

    # Then
    # the version is given a sha
    assert version.sha

    # and the correct feature states are cloned and added to the new version
    assert version.feature_states.count() == 2
    assert version.feature_states.filter(
        environment=environment, feature=feature, feature_segment=None, identity=None
    ).exists()
    assert version.feature_states.filter(
        environment=environment,
        feature=feature,
        feature_segment__segment=segment,
        identity=None,
    ).exists()

    # but the existing feature states are left untouched
    assert (
        FeatureState.objects.filter(environment_feature_version__isnull=True).count()
        == 2
    )
