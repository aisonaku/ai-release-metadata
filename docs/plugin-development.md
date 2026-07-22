# Plugin Development

The SDK's automatic metadata discovery is fully extensible. You can write custom plugins to extract deployment metadata from Kubernetes, Docker, AWS, or any proprietary internal system.

## The `MetadataPlugin` Protocol

To create a new plugin, you simply need to implement the `MetadataPlugin` protocol defined in `ai_release_metadata/plugins/base.py`. 

Because it uses a Python `Protocol`, you do not even need to inherit from a base class. Your class simply needs to expose an `extract()` method that returns a dictionary mapping standard schema keys to their values.

### Example: Kubernetes Plugin

Imagine you want to extract the deployment version from a Kubernetes Downward API mounted volume:

```python
from typing import Dict, Any

class KubernetesPlugin:
    """Extracts metadata from Kubernetes pod annotations."""
    
    def extract(self) -> Dict[str, Any]:
        metadata = {}
        annotation_path = "/etc/podinfo/annotations"
        
        try:
            with open(annotation_path, "r") as f:
                for line in f:
                    if line.startswith("deployment_version="):
                        val = line.split("=")[1].strip().strip('"')
                        metadata["deployment_version"] = val
        except FileNotFoundError:
            # Fails gracefully if not running in Kubernetes
            pass
            
        return metadata
```

## Using Custom Plugins

Once you have written your plugin, simply append it to the list when configuring the `MetadataProvider`. Remember that the *last* plugin evaluated takes precedence over earlier plugins.

```python
from ai_release_metadata import MetadataProvider
from ai_release_metadata.plugins import GitPlugin
from my_custom_plugins import KubernetesPlugin

# Kubernetes annotations will override any conflicting local Git state
MetadataProvider(plugins=[
    GitPlugin(),
    KubernetesPlugin()
])
```
