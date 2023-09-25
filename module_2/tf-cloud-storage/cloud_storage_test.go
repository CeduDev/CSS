package test

import (
	"testing"
	"strings"
	"os/exec"
	"fmt"

	"github.com/gruntwork-io/terratest/modules/terraform"
)

func TestTerraformStorageBucketWithEmptyFolder(t *testing.T) {
	// Specify the path to the Terraform configuration files.
	terraformOptions := &terraform.Options{
		// Set the path to the Terraform code that will be tested.
		TerraformDir: "./main.tf",
		Vars: map[string]interface{}{
			"bucket_name": "something_bad",
			"folder_name": "something_good",
		},
		// Variables to pass to our Terraform configuration using -var options
		// Variables can also be set using environment variables prefixed with TF_VAR_
		// EnvVars: map[string]string{
		//     "TF_VAR_bucket_name": "your_bucket_name",
		//     "TF_VAR_folder_name": "your_folder_name",
		// },
	}

	// Defer the destruction of resources until the test function returns.
	defer terraform.Destroy(t, terraformOptions)

	// Initialize and apply the Terraform configuration.
	terraform.InitAndApply(t, terraformOptions)

	// Get the bucket name and folder name from the Terraform output.
	bucketName := terraform.Output(t, terraformOptions, "bucket_name")
	folderName := terraform.Output(t, terraformOptions, "folder_name")

	// Verify that the storage bucket and folder exist.
	cmd := exec.Command("gsutil", "ls", fmt.Sprintf("gs://%s/%s", bucketName, folderName))
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("Error running 'gsutil ls': %v\nOutput:\n%s", err, output)
	}

	// Check if the folder exists in the bucket.
	expectedPath := fmt.Sprintf("gs://%s/%s/", bucketName, folderName)
	if !strings.Contains(string(output), expectedPath) {
		t.Errorf("Expected folder path %s not found in 'gsutil ls' output:\n%s", expectedPath, output)
	}
}
