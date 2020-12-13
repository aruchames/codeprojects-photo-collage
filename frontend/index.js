const imgPreview = {
  template: `<img id="img" :src="src">`,
  data() {
    return {
      src: "",
    };
  },
  props: ["file"],
  methods: {
    loadPicture(file) {
      let self = this;
      var reader = new FileReader();
      reader.onload = function (e) {
        self.src = e.target.result;
      };
      reader.readAsDataURL(file);
    },
    mounted() {
      this.loadPicture(this.file);
    },
  },
};

const FileUpload = {
  data() {
    return {
      inputFiles: [],
      orientation: "Vertical",
      loading: false,
      error: "",
      imgIds: [],
      jobId: "",
      finalImage: undefined,
      color: "#00FF00",
    };
  },
  methods: {
    handleNewFile(event) {
      this.inputFiles.push(event.target.files[0]);
      var req = fetch("http://172.18.232.75:5000/images", {
        method: "post",
        body: this.inputFiles[this.inputFiles.length - 1],
      });

      req
        .then(
          async (response) => {
            if (response.ok) return await response.text();
            return Promise.reject("Failed");
          },
          (rejected) => (this.error = rejected)
        )
        .then((text) => this.imgIds.push(text));

      console.log(this.imgIds);
    },
    submitStitch() {
      let req = fetch("http://172.18.232.75:5000/stitch", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ids: this.imgIds,
          orientation: this.orientation,
          border: 100,
          color: this.color,
        }),
      });

      req
        .then((response) => {
          if (response.ok) return response.text();
        })
        .then((jobId) => (this.jobId = jobId));
    },
    getStitch() {
      let req = fetch("http://172.18.232.75:5000/stitch", {
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          orientation: this.orientation,
          id: this.jobId,
        },
      });

      req
        .then((response) => {
          if (response.ok) {
            return response.text();
          }
          if (response.status == 202) {
            return null;
          }
        })
        .then((value) => {
          if (value) {
            this.finalImage = value;
            this.loading = false;
          }
        });
    },
  },
  components: {
    imgPreview: imgPreview,
  },
};

Vue.createApp(FileUpload).mount("#FileUpload");
