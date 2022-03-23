import hashlib
import time

from django.db import models
from django.db.models import Index
from django_lifecycle import AFTER_CREATE, BEFORE_CREATE, LifecycleModel, hook

from features.models import FeatureState
from segments.models import Segment


class EnvironmentFeatureVersion(LifecycleModel):
    sha = models.CharField(primary_key=True, max_length=64)
    environment = models.ForeignKey(
        "environments.Environment", on_delete=models.CASCADE
    )
    feature = models.ForeignKey("features.Feature", on_delete=models.CASCADE)
    live_from = models.DateTimeField(null=True)

    class Meta:
        indexes = [Index(fields=("environment", "feature"))]

    @hook(BEFORE_CREATE)
    def generate_sha(self):
        self.sha = hashlib.sha256(
            f"{self.environment.id}{self.feature.id}{time.time()}".encode("utf-8")
        ).hexdigest()

    @hook(AFTER_CREATE)
    def add_existing_feature_states(self):
        existing_environment_feature_state = (
            FeatureState.objects.filter(
                environment=self.environment,
                feature=self.feature,
                identity=None,
                feature_segment=None,
            )
            .order_by("-environment_feature_version__live_from")
            .first()
        )
        existing_environment_feature_state.clone(environment_feature_version=self)

        project_segments = Segment.objects.filter(project=self.environment.project)
        for segment in project_segments:
            existing_segment_override_feature_state = (
                FeatureState.objects.filter(
                    environment=self.environment,
                    feature=self.feature,
                    feature_segment__segment=segment,
                    identity=None,
                )
                .order_by("-environment_feature_version__live_from")
                .first()
            )
            if existing_segment_override_feature_state:
                existing_segment_override_feature_state.clone(
                    environment_feature_version=self
                )
