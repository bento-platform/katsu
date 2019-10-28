from rest_framework import serializers
from .models import *


class IndividualSerializer(serializers.ModelSerializer):

	class Meta:
		model = Individual
		fields = '__all__'
